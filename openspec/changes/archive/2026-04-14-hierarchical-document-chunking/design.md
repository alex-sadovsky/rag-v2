## Context

PDFs are loaded with `PyPDFLoader` in `app/services/rag.py`, which yields **one LangChain `Document` per page** with `metadata` including `source` and `page`. Today a single `RecursiveCharacterTextSplitter` splits the concatenation of all pages without enforcing page boundaries as parents. `POST /upload` calls `ingest_pdf`, which returns a **child chunk count** (vectors added). Hybrid BM25 in `app/services/hybrid_retrieval.py` dedupes using `source`, `page`, and a content hash prefix — hierarchical metadata must remain compatible with stable keys.

## Goals / Non-Goals

**Goals:**

- **Page-first hierarchy** — treat each page document as a **parent**; produce **child** chunks only from that page’s text.
- **Embed children** — Chroma stores **child** `Document`s only (same embedding model as today: `all-MiniLM-L6-v2`).
- **Rich metadata** — each child carries `source`, `page`, an index within the page, a marker for hierarchy level, and **full parent (page) text** in a dedicated metadata field for query-time grounding expansion.
- **Query behavior** — when building `[Passage i]` blocks, include **child text** plus **parent page context** from metadata in a clear, fixed template so the LLM sees both granularity and full-page background without silent truncation of the child alone.

**Non-Goals:**

- Replacing Chroma, changing the embedding model, or persisting the vector store across restarts.
- OCR, layout-aware sectioning, or heading-based splitting (PDF is not treated as Markdown).
- Async ingestion or background workers.
- Storing separate parent vectors in Chroma (parents are not embedded as standalone rows in this design).

## Decisions

### 1. Parent and child splitters

- **Parent unit** — one loaded `Document` per PDF page (existing loader behavior).
- **Child splitter** — `RecursiveCharacterTextSplitter` with configurable `chunk_size` and `chunk_overlap` (defaults: `chunk_size=1000`, `chunk_overlap=200` unless product prefers overlap `0` to stay closer to legacy behavior; design recommends modest overlap for continuity).

**Alternatives considered:**

- **Semantic chunking** — better boundaries but adds latency and deps; out of scope.
- **Fixed global 1000-char flat split** — current behavior; rejected as non-hierarchical.

### 2. Metadata schema (child documents)

Each child `Document` stored in Chroma SHALL include at least:

| Key | Purpose |
|-----|---------|
| `source` | PDF path/filename (existing) |
| `page` | 0-based page index from loader |
| `child_index` | 0-based index of this child within the page |
| `hierarchy` | literal `"child"` |
| `parent_page_content` | full text of the parent page (same as pre-split `Document.page_content` for that page) |

Optional: `parent_char_len` for debugging. Do not remove existing keys the loader already sets unless required.

**Storage note:** Duplicating `parent_page_content` on every child of a page increases metadata size; acceptable for course-scale PDFs and 5 MB limits. If memory becomes an issue later, a follow-up can store a hash + in-process cache.

### 3. Ingestion algorithm

```
docs = PyPDFLoader(path).load()
for each page_doc in docs:
    parent_text = page_doc.page_content
    children = child_splitter.split_documents([page_doc])
    for j, child in enumerate(children):
        merge metadata: hierarchy, child_index=j, parent_page_content=parent_text
add_documents(children_all)
invalidate_hybrid_index()
```

Return value `len(chunks)` remains the **number of child vectors** added (API contract unchanged).

### 4. Query / grounding template

In `run_rag_query`, for each retrieved `Document`:

- If `parent_page_content` is present and non-empty, build:

```
[Passage i — page {page+1}]
Fine-grained excerpt:
{child page_content}

Full page context:
{parent_page_content}
```

- If missing (legacy chunks in store during transition), fall back to current behavior: only `page_content`.

This avoids changing the REST response schema; `sources` entries continue to expose `content` and `metadata` for clients.

### 5. BM25 and deduplication

`chunk_dedupe_key` in `hybrid_retrieval.py` should remain valid. Child chunks differ in `page_content`; hash prefix still distinguishes them. No change required unless keys collide unexpectedly — monitor in tests.

### 6. Configuration

Add settings such as:

- `RAG_CHILD_CHUNK_SIZE` (default 1000)
- `RAG_CHILD_CHUNK_OVERLAP` (default 200)
- `RAG_INCLUDE_PARENT_IN_PROMPT` (default true) — allows A/B or emergency disable

## Risks / Trade-offs

- **Larger prompts** — including full page per passage increases tokens; mitigated by keeping `k` modest and existing caps.
- **Redundancy** — multiple retrieved children from the same page repeat `parent_page_content`; acceptable for correctness; optional later optimization to dedupe parent text per page in the prompt.

## Open Points

- Exact defaults for overlap should be validated against typical PDFs in the course.
- If any code path merges page documents before split, remove it so page boundaries stay authoritative.
