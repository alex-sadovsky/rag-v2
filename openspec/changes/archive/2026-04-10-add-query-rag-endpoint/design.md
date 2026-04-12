## Context

Ingestion stores chunked PDF text in an in-memory LangChain `Chroma` instance behind `get_vectorstore()` in `app/services/rag.py`, using `HuggingFaceEmbeddings` with `sentence-transformers/all-MiniLM-L6-v2`. Neighbor search for visualization already proves the store is queryable by embedding. This change adds a **question-answering** path: embed the question, retrieve similar chunks, then call **Claude Haiku 4.5** with explicit instructions to ground answers in those chunks only.

## Goals / Non-Goals

**Goals:**

- Expose `POST /query` with a JSON body containing the user question (and optionally retrieval parameters such as `k` if useful)
- Reuse the existing vector store and embedding stack — no second embedding model for retrieval
- Use Claude Haiku 4.5 as the generator; default model id **`claude-haiku-4-5`** (Anthropic API alias), overridable via config
- Read **`ANTHROPIC_API_KEY`** from the environment (via `pydantic-settings`, consistent with the rest of the app)
- Implement a clear **grounding** system prompt: answer from context only; if context does not contain the answer, say so clearly

**Non-Goals:**

- Removing or replacing the vector visualization / export / UMAP endpoints
- Persistent Chroma across restarts or cloud-hosted vector DB
- Streaming responses (can be a follow-up)
- Hybrid retrieval (BM25 + dense), re-ranking, or citation offsets back into PDF pages (unless trivially included in chunk metadata already)
- Changing ingestion chunk size or embedding model

## Decisions

### Endpoint shape: `POST /query`

Mirrors the existing top-level `POST /upload` style. Request body includes at least `question: str`. Response includes at least the model’s answer string; optionally include `sources` (chunk excerpts or metadata) for transparency and debugging.

**Alternatives considered:** `POST /api/rag/query` — clearer grouping but user asked explicitly for `/query`.

### Retrieval: `similarity_search` (or `similarity_search_with_score`) on the shared `Chroma` instance

Use the same `get_vectorstore()` as ingestion. Default **k** in a sensible range (e.g. 4–6); expose as an optional request field with a cap to avoid huge prompts.

### LLM integration: LangChain `ChatAnthropic` from `langchain-anthropic`

Aligns with existing LangChain + Chroma usage. Instantiate with `api_key` from settings and `model` from settings (default `claude-haiku-4-5`).

**Alternatives considered:** Raw `anthropic` SDK — fewer dependencies but duplicates patterns already established by LangChain in the project.

### Configuration

- `anthropic_api_key: str | None = None` — if missing at runtime, return **503** (or **401**-style configuration error) on `/query` with a clear message rather than failing obscurely inside the client
- `anthropic_model: str = "claude-haiku-4-5"` — allows future model bumps without code changes

Environment variable names: `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` (optional).

### Grounding prompt (conceptual)

System (or equivalent) instructions should:

1. State that the assistant must only use the provided “Context” passages.
2. Require concise, accurate answers; no invented facts beyond context.
3. If context is empty or irrelevant, respond that the documents do not contain enough information.

User message combines the retrieved chunk texts (with light separators or labels) and the user question.

### Empty vector store

If there are no documents (or retrieval returns no chunks), still call the model only if product-wise acceptable — **prefer** short-circuiting with a clear message that nothing is indexed, to save cost and latency. Document the chosen behavior in code and tests.

## Risks / Trade-offs

- **API key required** — local dev must set `ANTHROPIC_API_KEY`; CI tests should mock the LLM and optionally skip integration tests without a key.
- **Cost and latency** — every query hits Anthropic; retrieval k and max context length should stay bounded.
- **Hallucination** — grounding prompt reduces but does not eliminate risk; keeping answers strictly tied to retrieved text is the main mitigation.
- **In-memory store** — answers only reflect content ingested in the current process lifetime, same limitation as today.
