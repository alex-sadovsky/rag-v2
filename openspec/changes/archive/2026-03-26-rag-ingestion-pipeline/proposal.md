## Why

Uploaded PDFs are currently stored on disk but never processed — they can't be searched or queried. Adding a RAG ingestion pipeline makes document content immediately available for semantic retrieval after each upload.

## What Changes

- New `app/services/rag.py` module with a synchronous ingestion pipeline
- Pipeline is triggered inside `POST /upload` after the file is saved to disk
- PDF is loaded from disk, split into chunks (size 1000), embedded with `all-MiniLM-L6-v2`, and stored in an in-memory Chroma vector store
- Chroma vector store lives as a module-level singleton for the application lifetime
- Upload response extended to include the number of ingested chunks
- New dependencies: `langchain`, `langchain-community`, `langchain-chroma`, `sentence-transformers`, `pypdf`, `chromadb`

## Capabilities

### New Capabilities

- `rag-ingestion`: Splits, embeds, and indexes a PDF into the in-memory Chroma vector store after upload

### Modified Capabilities

- `pdf-upload`: Upload response now includes `chunks` count; pipeline is called synchronously before returning

## Impact

- `app/services/rag.py` — new file
- `app/routers/upload.py` — calls `ingest_pdf()` after saving, returns chunk count
- `pyproject.toml` — 6 new dependencies
- First request triggers model download (~90 MB); subsequent requests use cached model
- Memory usage increases with total ingested content (in-memory Chroma)
