"""Conditional hybrid retrieval: dense-first; BM25 only when dense is weak and lexical warrant passes."""

from __future__ import annotations

import hashlib
import re
from typing import TYPE_CHECKING

from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from app.config import Settings

if TYPE_CHECKING:
    from langchain_chroma import Chroma

# English stopwords (minimal list for token counting / lexical gate).
_EN_STOP = frozenset(
    """
    a an the and or but if as of at by for from in into is it its no not on such that their
    then there these they this to was will with about after again against all am any are be been
    being both can did do does doing down during each few further had has have having he her here
    hers herself him himself his how i if in into is it its itself just me more most my myself
    no nor not of off on once only other our ours ourselves out over own same she should so some
    such than that the their theirs them themselves then there these they this those through to
    too under until up very was we were what when where which while who whom why with would you
    your yours yourself yourselves
    """.split()
)

_bm25_cache: tuple[BM25Okapi, list[Document]] | None = None


def invalidate_hybrid_index() -> None:
    """Drop cached BM25 state so the next hybrid query rebuilds from Chroma."""
    global _bm25_cache
    _bm25_cache = None


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text.lower())


def chunk_dedupe_key(doc: Document) -> str:
    md = dict(doc.metadata) if doc.metadata else {}
    src = str(md.get("source", ""))
    page = str(md.get("page", ""))
    h = hashlib.sha256((doc.page_content or "")[:512].encode()).hexdigest()[:16]
    return f"{src}|{page}|{h}"


def weak_dense_signal(distances: list[float], settings: Settings) -> bool:
    """True when the best (minimum) Chroma distance is still above the weak threshold."""
    if not distances:
        return False
    best = min(distances)
    return best > settings.query_dense_weak_best_distance_gt


def lexical_warranted(question: str, settings: Settings) -> bool:
    """Deterministic lexical warrant: quoted span, identifier-like tokens, or enough content words."""
    q = question.strip()
    if not q:
        return False

    if settings.query_lexical_enable_quotes and (
        re.search(r'"[^"]{2,}"', q) or re.search(r"'[^']{2,}'", q)
    ):
        return True

    if settings.query_lexical_enable_identifiers:
        if re.search(r"\d", q):
            return True
        if re.search(r"\b[a-z]+[A-Z][a-zA-Z]*\b", q):
            return True
        if re.search(r"\b[A-Z]{2,}\b", q):
            return True
        if re.search(r"\b\w+-\w+\b", q):
            return True

    tokens = tokenize(q)
    content = [t for t in tokens if t not in _EN_STOP and len(t) >= 2]
    return len(content) >= settings.query_lexical_min_alpha_tokens


def _get_bm25_and_documents(store: Chroma) -> tuple[BM25Okapi, list[Document]]:
    global _bm25_cache
    if _bm25_cache is not None:
        return _bm25_cache

    raw = store._collection.get(include=["documents", "metadatas"])
    texts = raw["documents"] or []
    metas = raw["metadatas"] or []
    documents: list[Document] = []
    for text, meta in zip(texts, metas, strict=False):
        if text is None:
            continue
        documents.append(Document(page_content=text, metadata=dict(meta or {})))

    tokenized_corpus = [
        tokenize(d.page_content or "") or ["empty"] for d in documents
    ]
    bm25 = BM25Okapi(tokenized_corpus)
    _bm25_cache = (bm25, documents)
    return _bm25_cache


def bm25_top_k(question: str, store: Chroma, k: int) -> list[Document]:
    bm25, documents = _get_bm25_and_documents(store)
    if not documents:
        return []
    q_tokens = tokenize(question)
    if not q_tokens:
        return []
    scores = bm25.get_scores(q_tokens)
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    return [documents[i] for i in ranked]


def fuse_dense_first(
    dense_docs: list[Document],
    bm25_docs: list[Document],
    k: int,
) -> list[Document]:
    """Preserve dense order; append BM25-only chunks in BM25 order until length k."""
    seen: set[str] = set()
    out: list[Document] = []
    for d in dense_docs:
        key = chunk_dedupe_key(d)
        if key not in seen:
            seen.add(key)
            out.append(d)
            if len(out) >= k:
                return out
    for d in bm25_docs:
        key = chunk_dedupe_key(d)
        if key not in seen:
            seen.add(key)
            out.append(d)
            if len(out) >= k:
                break
    return out


def retrieve_chunks_conditional(
    question: str,
    k: int,
    store: Chroma,
    settings: Settings,
) -> tuple[list[Document], bool]:
    """
    Dense-first retrieval; run BM25 and fuse only when weak_dense ∧ lexical_warranted.

    Returns (documents_for_prompt, used_bm25_supplement).
    """
    pairs = store.similarity_search_with_score(question, k=k)
    if not pairs:
        return [], False

    dense_docs = [d for d, _ in pairs]
    distances = [float(s) for _, s in pairs]

    weak = weak_dense_signal(distances, settings)
    lex = lexical_warranted(question, settings)
    if not (weak and lex):
        return dense_docs, False

    bm25_hits = bm25_top_k(question, store, k=k)
    fused = fuse_dense_first(dense_docs, bm25_hits, k)
    return fused, True
