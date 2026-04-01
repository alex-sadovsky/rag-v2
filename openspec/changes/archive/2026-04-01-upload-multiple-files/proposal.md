## Why

The `/upload` endpoint currently accepts a single PDF file per request, forcing API callers to make N sequential requests to ingest N documents. Supporting batch uploads reduces client complexity and enables more efficient ingestion workflows.

## What Changes

- `POST /upload` now accepts up to 50 PDF files per request (multipart form)
- Each file is independently validated (PDF, < 5 MB), saved, and ingested
- Ingestion is best-effort: one file failing does not abort the rest
- Response changes from a single object to a list of per-file results, each with either `chunks` (success) or `error` (failure)
- Requests with 0 or > 50 files are rejected with HTTP 400

**BREAKING**: Response schema changes from `{ filename, chunks }` to `[{ filename, chunks|error }, ...]`

## Capabilities

### New Capabilities
- `batch-upload`: Accept, validate, save, and ingest multiple PDF files in one request with per-file result reporting

### Modified Capabilities
- `pdf-upload`: Existing upload requirement changes — single file → batch (1–50 files), response schema updated to list

## Impact

- `app/routers/upload.py` — parameter type, validation logic, response model, ingestion loop
- `app/services/rag.py` — no changes (ingest_pdf used as-is per file)
- API contract change (breaking) for any existing callers of `POST /upload`
