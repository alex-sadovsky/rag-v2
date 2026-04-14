## Why

The ingestion pipeline today uses a single flat `RecursiveCharacterTextSplitter` (1000 characters, no overlap) over whole PDF loads. That mixes structure across page boundaries and does not preserve a **document hierarchy** (page → passage) that retrieval and grounding can exploit. **Hierarchical chunking** indexes **fine-grained child chunks** for embedding similarity while retaining **parent context** (per-page scope) so answers can be grounded in both precise matches and broader page-level text.

## What Changes

- **Ingestion (`app/services/rag.py`)** switches from one flat split to a **two-level hierarchy**: each PDF page is a **parent** unit; each page is split into **child** chunks with configurable size and overlap suitable for dense retrieval.
- **Metadata** on every stored chunk SHALL include hierarchy fields: at minimum `page`, `source`, child index within the page, and **parent page text** (or an equivalent reference) for downstream use.
- **Query grounding (`app/services/query.py`)** SHALL, when assembling context for the LLM, **use hierarchical metadata** so passages shown to the model include both the retrieved child text and the associated parent page context in a documented, non-duplicative way (e.g. labeled sections per passage).
- **Configuration** (`app/config.py`): optional settings for child chunk size, overlap, and toggles for parent-context expansion — with defaults that approximate current behavior in total token budget where reasonable.
- **Specification**: delta updates to `rag-ingestion` (and any affected capability) describing hierarchical ingestion and parent-aware grounding.

## Capabilities

### New Capabilities

- None (extends existing ingestion and query behavior).

### Modified Capabilities

- `rag-ingestion`: Replace flat fixed-size splitting with hierarchical page → child splitting and required metadata.
- `rag-query` (or query-facing spec if present): Grounding SHALL incorporate parent context from chunk metadata when present.

## Impact

- `app/services/rag.py` — core chunking refactor.
- `app/services/query.py` — context assembly uses hierarchical metadata.
- `app/config.py` — optional chunking parameters.
- `tests/` — ingestion and/or query tests for metadata and context shape.
- `openspec/specs/` — merge spec deltas during apply or archive workflow.
