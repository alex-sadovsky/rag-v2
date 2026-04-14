## Why

Dense-only retrieval in `POST /query` is fast and simple, but it can miss exact lexical matches (rare tokens, acronyms, identifiers) and may return marginally relevant chunks when embedding similarity is uniformly weak. Unconditional hybrid search (always merging BM25 and dense) adds latency and complexity on every request. A **conditional** strategy—**dense-first**, then **BM25 only when dense results look weak and the query warrants lexical matching**—targets extra cost and code paths at the cases that benefit most.

## What Changes

- **`POST /query` retrieval pipeline** becomes **dense-first**: always run embedding similarity against the existing Chroma store (same model as ingestion).
- **BM25 (lexical) retrieval** runs **only if both**:
  - **Weak dense signal** — top retrieved scores/distances indicate low confidence (configurable threshold), and
  - **Lexical search** — a lightweight, deterministic heuristic (or documented rules) decides the question is likely to benefit from term-based matching.
- **Fusion** — when BM25 runs, merge lexical candidates with dense results using a documented strategy (e.g. deduplication, score-agnostic ordering such as RRF or “dense order first, append BM25-only hits”), capped to the same overall `k` (or a slightly larger fused cap documented in design).
- **Configuration** — environment-driven thresholds for “weak dense” and toggles for lexical heuristics where appropriate; defaults chosen to be conservative (BM25 rarely triggered) to preserve current behavior unless signals warrant it.
- **Dependencies** — add a small BM25 stack (e.g. `rank-bm25` plus tokenization, or LangChain `BM25Retriever`) and any utilities needed to build an in-memory index from indexed chunks.

## Capabilities

### New Capabilities

- `rag-query`: Extend retrieval behavior with optional conditional BM25 when dense results are weak and lexical matching is indicated.

### Modified Capabilities

- `app-config`: Optional settings for weak-dense thresholds and lexical/BM25 behavior.

## Impact

- `app/services/query.py` — retrieval orchestration (dense with scores → gate → optional BM25 → fuse).
- `app/services/rag.py` or a small new module — BM25 index lifecycle aligned with the in-memory Chroma store (build/refresh when documents exist).
- `app/config.py` — new optional settings.
- `pyproject.toml` — BM25-related dependency.
- `tests/test_query.py` — unit tests for gating and fusion with mocks.
- `openspec/specs/rag-query/spec.md` — new requirements for conditional hybrid retrieval (via change spec delta).
