## Context

The FastAPI boilerplate already has a router infrastructure (`app/routers/`). This change adds a `POST /upload` endpoint that accepts a PDF file via multipart form, validates it, and saves it to a local `uploads/` directory. No external dependencies are needed — FastAPI's built-in `UploadFile` handles multipart.

## Goals / Non-Goals

**Goals:**
- Accept a single PDF file via `POST /upload` (multipart/form-data)
- Reject files larger than 5 MB with HTTP 413
- Reject non-PDF files (wrong MIME type or extension) with HTTP 415
- Save accepted files to `uploads/` directory, created automatically if absent
- Return the saved filename in the response

**Non-Goals:**
- Virus scanning or deep content inspection
- Cloud/remote storage (S3, GCS, etc.)
- Multiple file upload in one request
- File deduplication or indexing
- Authentication/authorization on the endpoint

## Decisions

### File validation: MIME type + extension check
Check both `content_type == "application/pdf"` and that the filename ends with `.pdf`. Checking only MIME type can be spoofed by clients; checking only extension can miss misnamed files.

**Alternatives considered:**
- Magic bytes inspection (`%PDF-` header): more accurate but adds complexity — out of scope for now

### Size limit: read-and-check via `UploadFile.read()`
Read up to `MAX_SIZE + 1` bytes and compare length. If over limit, reject before writing to disk.

**Alternatives considered:**
- `Content-Length` header check: unreliable — clients can omit or lie about it
- Streaming write with abort: correct but more complex; read-and-check is simpler for 5 MB cap

### Storage: flat `uploads/` directory, preserve original filename
Save files using their original filename. Simple and transparent for local development.

**Alternatives considered:**
- UUID-based filenames: avoids collisions but loses the original name — not needed for local dev
- Subdirectory per date: adds structure but complicates retrieval; out of scope

### Uploads directory: configured via `Settings`, created at startup
Add `uploads_dir: str = "uploads"` to `app/config.py`. Create the directory in `app/main.py` lifespan or on first request.

## Risks / Trade-offs

- **Filename collision** → Existing file is silently overwritten. Acceptable for local dev; document the behavior.
- **5 MB read into memory** → For a 5 MB cap this is fine; would need streaming for larger limits.
- **No auth on endpoint** → Anyone with network access can upload. Acceptable for local-only use.
