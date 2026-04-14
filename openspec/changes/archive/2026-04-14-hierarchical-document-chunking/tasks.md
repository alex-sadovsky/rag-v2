## 1. Configuration

- [x] 1.1 Add optional settings to `app/config.py`: child chunk size, child chunk overlap, and a boolean to include parent page text in the query prompt (all with safe defaults documented in `Settings`).
- [x] 1.2 Wire environment variable names consistently with existing style (e.g. `RAG_*` prefixes).

## 2. Hierarchical ingestion

- [x] 2.1 Refactor `app/services/rag.py` to split **per loaded page document** using `RecursiveCharacterTextSplitter` with settings from configuration.
- [x] 2.2 For each child chunk, set metadata: `hierarchy` = `child`, `child_index` (0-based within page), `parent_page_content` = full parent page text, preserving `source` and `page` from the loader.
- [x] 2.3 Keep `ingest_pdf` return value as the **number of child chunks** indexed; call `invalidate_hybrid_index()` after adds (existing behavior).

## 3. Query grounding

- [x] 3.1 Update `app/services/query.py` to build each context passage using the template from design: child excerpt plus full page context when `parent_page_content` is present; otherwise fall back to child-only (backward compatibility).
- [x] 3.2 Respect `RAG_INCLUDE_PARENT_IN_PROMPT` (or chosen setting name) when false — child-only passages.

## 4. Tests and verification

- [x] 4.1 Add or extend tests to assert child metadata includes `parent_page_content` and `child_index` after ingestion (mock or small fixture PDF).
- [x] 4.2 Add tests that `run_rag_query` prompt assembly includes parent context when metadata is set (mock retriever/store as needed).
- [x] 4.3 Run existing test suite; fix any breaks from chunk count or metadata shape.

## 5. Specification

- [x] 5.1 Apply the spec deltas in `openspec/changes/hierarchical-document-chunking/specs/` to `openspec/specs/rag-ingestion/spec.md` and `openspec/specs/rag-query/spec.md` during implementation (or merge as part of archive workflow).
