## Why

The app indexes PDFs into Chroma and exposes vector-space tooling (export, UMAP, neighbors), but there is no path that answers natural-language questions using those chunks. That keeps the project in “embedding explorer” territory instead of a complete RAG loop. A dedicated query endpoint closes the loop: retrieve relevant passages, ground an LLM on them, and return a synthesized answer.

## What Changes

- New `POST /query` endpoint that accepts a user question (JSON body)
- Server retrieves top-k relevant chunks from the existing in-memory Chroma store using the same embedding model as ingestion (`all-MiniLM-L6-v2`)
- Retrieved chunk text is passed to **Anthropic Claude Haiku 4.5** via a **grounding prompt** that instructs the model to rely only on the provided context and to admit when context is insufficient
- Anthropic API credentials supplied through environment variables (API key required; optional model override)
- New dependency for the Anthropic / LangChain integration (e.g. `langchain-anthropic`)

## Capabilities

### New Capabilities

- `rag-query`: Accept a question, retrieve chunks from Chroma, generate a grounded answer with Claude Haiku 4.5

### Modified Capabilities

- `app-config`: New settings for Anthropic API key and optional model id

## Impact

- `pyproject.toml` — add `langchain-anthropic` (or equivalent Anthropic client stack used in code)
- `app/config.py` — `ANTHROPIC_API_KEY`, optional `ANTHROPIC_MODEL` (default Haiku 4.5 alias)
- `app/services/rag.py` (or new `app/services/query.py`) — retrieval + prompt assembly + LLM call
- `app/routers/` — new router or route for `POST /query`, registered from `app/routers/__init__.py`
- `tests/` — tests with mocked vectorstore and/or LLM where appropriate
- Existing upload and vector visualization flows remain unchanged
