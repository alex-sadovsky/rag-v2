from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator

from app.config import settings
from app.services.query import run_rag_query

router = APIRouter()


class QueryRequest(BaseModel):
    """Body for ``POST /query``: natural-language question and optional retrieval size."""

    question: str = Field(
        ...,
        min_length=1,
        description="User question; embedded and matched against indexed PDF chunks.",
    )
    k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of vector chunks to retrieve (similarity search).",
    )

    @model_validator(mode="after")
    def strip_question_non_empty(self):
        q = self.question.strip()
        if not q:
            raise ValueError("question must not be empty or whitespace-only")
        self.question = q
        return self


class SourceChunk(BaseModel):
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class QueryResponse(BaseModel):
    """Grounded answer and the retrieved passages used for context (debugging / transparency)."""

    answer: str
    sources: list[SourceChunk]


@router.post(
    "/query",
    response_model=QueryResponse,
    responses={
        503: {
            "description": "Anthropic API is not configured (missing `ANTHROPIC_API_KEY`).",
        },
    },
    summary="RAG query over indexed PDFs",
)
def query_rag_endpoint(body: QueryRequest) -> QueryResponse:
    """Answer a question using Chroma retrieval and Claude Haiku 4.5 with a grounding prompt."""
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY is not configured. Set it in the environment to enable queries.",
        )

    result = run_rag_query(body.question, k=body.k, settings=settings)
    return QueryResponse(
        answer=result.answer,
        sources=[SourceChunk(**s) for s in result.sources],
    )
