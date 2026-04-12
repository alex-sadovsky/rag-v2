## 1. Dependencies and configuration

- [x] 1.1 Add BM25 dependency (`rank-bm25` and tokenizer choice, or `langchain-community` BM25 retriever stack as chosen in design) to `pyproject.toml`
- [x] 1.2 Extend `app/config.py` with optional settings: weak-dense threshold(s), lexical heuristic parameters (e.g. min tokens, enable quoted-phrase detection), and any fusion cap — all with safe defaults
- [x] 1.3 Install dependencies into the project environment

## 2. Lexical index and gating helpers

- [x] 2.1 Implement a small module or functions to (re)build an in-memory BM25 index from the same texts Chroma searches (e.g. via `collection.get()` including documents/metadata)
- [x] 2.2 Hook index invalidation into the ingestion path (`ingest_pdf` / `add_documents`) so BM25 stays consistent with Chroma in-process
- [x] 2.3 Implement `weak_dense_signal` from `similarity_search_with_score` results using configured thresholds
- [x] 2.4 Implement `lexical_warranted(query)` per the documented heuristic rules

## 3. Query service integration

- [x] 3.1 Refactor `run_rag_query` to: dense retrieval with scores → if `weak ∧ lexical_warranted` then BM25 retrieval → fuse results (dense-first policy) → existing grounding prompt assembly and `ChatAnthropic` call unchanged
- [x] 3.2 Ensure empty store and empty retrieval paths remain clear and tested
- [x] 3.3 Optionally log or attach debug info when BM25 path runs (only if it does not break API contract without opt-in)

## 4. HTTP API and docs

- [x] 4.1 Keep `POST /query` backward compatible (`question`, `k`); document any new optional fields if added
- [x] 4.2 Update README `/query` section to describe conditional hybrid retrieval at a high level

## 5. Specification

- [x] 5.1 Apply the spec delta in `openspec/changes/conditional-hybrid-query-retrieval/specs/rag-query/spec.md` to `openspec/specs/rag-query/spec.md` during implementation (or merge as part of archive workflow)

## 6. Verification

- [x] 6.1 Unit tests: mock Chroma scores to force weak/non-weak paths; assert BM25 is skipped unless both gates pass
- [x] 6.2 Unit tests: lexical heuristic boundaries (quoted phrase, acronym-like tokens, etc.)
- [x] 6.3 Unit tests: fusion deduplication and final list length cap relative to `k`
