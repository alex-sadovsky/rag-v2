from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator

from app.config import settings
from app.services.disaster_query import is_natural_disaster_query, run_disaster_query
from app.services.query import run_rag_query

router = APIRouter()

_DISASTER_SOURCE_PROVENANCE = (
    "Answer produced from bundled EM-DAT-style CSV data (same logic as MCP tool "
    "`query_natural_disasters`; see `dataset/csv/`)."
)


class QueryRequest(BaseModel):
    """Body for ``POST /query``: natural-language question and optional retrieval size."""

    question: str = Field(
        ...,
        min_length=1,
        description=(
            "User question. Normally embedded and matched against indexed PDF chunks (RAG). "
            "If the question clearly targets global natural-disaster records (EM-DAT-style), "
            "the server answers from `dataset/csv/` via the same query path as MCP "
            "`query_natural_disasters` instead of vector search."
        ),
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
        400: {"description": "Invalid parameters for the natural-disaster CSV query."},
        503: {
            "description": (
                "Anthropic API is not configured for RAG, disaster CSV data unavailable, "
                "or other server-side dependency missing."
            ),
        },
    },
    summary="Query: RAG over PDFs or EM-DAT-style disaster CSV",
)
def query_rag_endpoint(body: QueryRequest) -> QueryResponse:
    """Answer using vector RAG (Claude + Chroma) or, for disaster-data questions, EM-DAT CSV query."""
    if is_natural_disaster_query(body.question, settings):
        try:
            text = run_disaster_query(body.question, settings)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except (FileNotFoundError, OSError) as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Disaster dataset unavailable: {exc}",
            ) from exc
        return QueryResponse(
            answer=text,
            sources=[
                SourceChunk(
                    content=_DISASTER_SOURCE_PROVENANCE,
                    metadata={
                        "kind": "emdat_csv",
                        "tool": "query_natural_disasters",
                    },
                )
            ],
        )

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
