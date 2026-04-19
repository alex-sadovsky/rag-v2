## Why

The `POST /upload` endpoint currently caps each PDF at 5 MB. Users with larger documents (scanned books, image-heavy PDFs) hit this limit unnecessarily for a local RAG demo. Raising the per-file cap to 50 MB improves usability while keeping a bounded upper limit.

## What Changes

- Per-file maximum size increases from 5 MB to **50 MB** (50 × 1024 × 1024 bytes).
- User-facing error text and any documentation that mention "5 MB" are updated to **50 MB**.
- Specs under `pdf-upload` and `batch-upload` are updated so scenarios and requirements reference the new limit.

**Non-breaking (API contract):** Response shape and status codes for valid requests are unchanged; only the size threshold and error messages change.

## Capabilities

### Modified Capabilities

- `pdf-upload`: File size limit and related scenarios (successful upload, oversized, exactly at limit).
- `batch-upload`: Scenarios that reference per-file size under the limit.

## Impact

- `app/routers/upload.py` — `MAX_FILE_SIZE` constant and `ValueError` message.
- `README.md` — limits section if it states 5 MB per file.
- `openspec/specs/pdf-upload/spec.md` and `openspec/specs/batch-upload/spec.md` — apply during archive/merge per project workflow.
