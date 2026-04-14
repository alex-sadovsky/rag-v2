from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from langchain_core.documents import Document

from app.config import Settings
from app.services.hybrid_retrieval import retrieve_chunks_conditional
from app.services.rag import get_vectorstore

GROUNDING_SYSTEM = """You are a careful assistant that answers using ONLY the provided context passages below.
If the answer is not contained in the context, say clearly that the indexed documents do not contain enough information to answer.
Do not invent facts, citations, or details not supported by the context.
Keep answers concise unless the question requires detail."""


def _format_context_passage(
    index: int,
    doc: Document,
    settings: Settings,
) -> str:
    """Build one grounding block: hierarchical (child + parent page) or legacy child-only."""
    md = dict(doc.metadata) if doc.metadata else {}
    parent = md.get("parent_page_content")
    use_parent = (
        settings.rag_include_parent_in_prompt
        and isinstance(parent, str)
        and parent.strip() != ""
    )
    if use_parent:
        raw_page = md.get("page", 0)
        try:
            page_display = int(raw_page) + 1
        except (TypeError, ValueError):
            page_display = 1
        return (
            f"[Passage {index} — page {page_display}]\n"
            f"Fine-grained excerpt:\n{doc.page_content}\n\n"
            f"Full page context:\n{parent}"
        )
    return f"[Passage {index}]\n{doc.page_content}"


@dataclass(frozen=True)
class QueryResult:
    answer: str
    sources: list[dict[str, Any]]


def run_rag_query(
    question: str,
    *,
    k: int,
    settings: Settings,
) -> QueryResult:
    """Retrieve chunks from Chroma and answer with a grounded Claude Haiku call.

    Caller must ensure ``settings.anthropic_api_key`` is set.
    """
    store = get_vectorstore()
    if int(store._collection.count()) == 0:
        return QueryResult(
            answer="No documents have been indexed yet. Upload PDFs before querying.",
            sources=[],
        )

    docs, _used_bm25 = retrieve_chunks_conditional(
        question, k=k, store=store, settings=settings
    )
    if not docs:
        return QueryResult(
            answer="No relevant passages were retrieved from the indexed documents.",
            sources=[],
        )

    context_blocks = []
    sources: list[dict[str, Any]] = []
    for i, doc in enumerate(docs, start=1):
        context_blocks.append(_format_context_passage(i, doc, settings))
        sources.append(
            {
                "content": doc.page_content,
                "metadata": dict(doc.metadata) if doc.metadata else {},
            }
        )

    context_text = "\n\n".join(context_blocks)
    user_content = (
        f"Context from indexed documents:\n\n{context_text}\n\n"
        f"Question: {question.strip()}"
    )

    llm = ChatAnthropic(
        model=settings.anthropic_model,
        anthropic_api_key=settings.anthropic_api_key,
    )
    response = llm.invoke(
        [
            SystemMessage(content=GROUNDING_SYSTEM),
            HumanMessage(content=user_content),
        ]
    )
    answer = (response.content or "").strip()
    return QueryResult(answer=answer, sources=sources)
