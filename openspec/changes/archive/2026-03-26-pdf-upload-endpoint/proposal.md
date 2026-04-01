## Why

The application needs to accept PDF documents from clients and store them locally for further processing. A dedicated upload endpoint provides a controlled, validated ingestion point for document data.

## What Changes

- New `POST /upload` endpoint that accepts a single PDF file via multipart form upload
- Uploaded files are saved to a configurable local directory (`uploads/`)
- File size is validated server-side: PDFs exceeding 5 MB are rejected
- Non-PDF files are rejected based on content type and file extension

## Capabilities

### New Capabilities

- `pdf-upload`: Accepts, validates, and stores a single PDF file via `POST /upload`

### Modified Capabilities

- `api-router`: New upload router must be registered alongside the existing health router

## Impact

- New dependency: none (FastAPI's `UploadFile` is built-in)
- New router: `app/routers/upload.py`
- New uploads directory: `uploads/` (created at startup if absent)
- `app/routers/__init__.py` updated to include the upload router
