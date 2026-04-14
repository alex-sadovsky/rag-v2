## Context

Indexed chunks live in an in-memory LangChain `Chroma` instance (`get_vectorstore()` in `app/services/rag.py`) with `HuggingFaceEmbeddings` (`sentence-transformers/all-MiniLM-L6-v2`). `run_rag_query` in `app/services/query.py` currently calls `similarity_search` without scores. This change keeps **Claude Haiku 4.5** grounding unchanged but upgrades **retrieval** to a **conditional hybrid** flow.

## Goals / Non-Goals

**Goals:**

- **Dense-first** — every query performs dense (embedding) retrieval first; this remains the primary ranking signal.
- **BM25 only when** `weak_dense ∧ lexical_warranted` — no standalone BM25-only path for normal queries; BM25 is a **conditional supplement**.
- **Deterministic gating** — weak-dense and lexical rules are testable and configurable (no LLM-in-the-loop for routing).
- **Bounded work** — BM25 index built from the same chunk set as Chroma; cap BM25 candidate count and final fused list to avoid prompt blowups.
- **Observable behavior** — optional debug metadata (e.g. whether BM25 ran) is acceptable if exposed via response model or logs; not required for MVP if it complicates the API contract.

**Non-Goals:**

- Replacing Chroma or changing the default embedding model.
- Full cross-encoder re-ranking or learning-to-rank.
- Persistent lexical indexes across process restarts (in-memory only, consistent with Chroma today).
- Streaming responses.

## Decisions

### 1. Dense retrieval with scores

Use `similarity_search_with_score` (or equivalent) so each chunk has a **distance or similarity** used only for the **weak** gate. Document how Chroma’s metric is interpreted (e.g. L2 distance: lower is better; define `weak` as “best-of-k distance above τ” or “all k distances above τ’” — pick one rule and stick to it in tests).

### 2. Weak dense signal

Define **weak** using configurable thresholds, for example:

- `QUERY_DENSE_WEAK_MAX_BEST_DISTANCE` — if the **best** retrieved distance exceeds this, dense is weak; or
- Normalize using min/max of the batch if you prefer relative spread (slightly more complex; document clearly).

Default thresholds should err on the side of **not** calling BM25 until tuned with real data.

### 3. Lexical warrant (“lexical search”)

BM25 runs only if **lexical_warranted(query)** is true. Use a **simple, fast heuristic**, for example any of:

- Query contains **quoted** segments (exact phrase intent).
- Query contains **identifiers**: digits, hyphens, CamelCase tokens, or all-caps acronyms of length ≥ 2.
- Query has at least **N** alphanumeric tokens after stopword filtering (N configurable).

The design should list the exact rules implemented so behavior is stable across releases.

### 4. BM25 index lifecycle

Maintain an in-memory BM25 corpus **mirroring** documents in the vector store:

- **Build** on first query after ingestion or lazily on first BM25-eligible query once `count() > 0`.
- **Invalidate / rebuild** when new documents are added (`ingest_pdf` / `add_documents`) in the same process — simplest approach: rebuild from `collection.get()` or from stored `Document` list if the app keeps one; if rebuild is expensive, document batching for a follow-up.

### 5. Fusion strategy (dense-first)

When BM25 runs:

- Take dense-ranked list as **primary**.
- Add BM25-ranked chunks that are **not** already present (match by stable id: e.g. `metadata` source + chunk hash or page + offset if available).
- **Cap** final list to `k` (request’s `k`) or to `min(k, k_fused)` with `k_fused` documented.
- Optional: **RRF** over two ranked lists for ordering when both contribute; if simpler, **preserve dense order** and append new BM25-only chunks in BM25 order until the cap.

### 6. API surface

- Reuse existing `POST /query` body fields (`question`, `k`) unless a **feature flag** or optional `debug` field is needed; prefer **no new required fields** so clients stay compatible.

### 7. Library choice

Prefer **`rank-bm25`** with explicit tokenization **or** LangChain **`BM25Retriever`** — choose one that minimizes duplication with existing LangChain `Document` types and stays lightweight.

## Risks / Trade-offs

- **Heuristic lexical gate** may misfire; defaults should be conservative.
- **Rebuilding BM25** on each ingest could add latency for large corpora; acceptable for course-scale data; document complexity if rebuild becomes hot.
- **Score semantics** differ between dense distance and BM25 scores; fusion should not naïvely sum scores without normalization (hence RRF or order-based fusion).

## Open Points

- Exact Chroma distance metric and threshold names should be verified against `langchain-chroma` / Chroma defaults during implementation.
- If chunk identity for deduplication is weak in metadata, define a fallback (content hash prefix).
