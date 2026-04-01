## Context

The `/upload` endpoint currently accepts a single `UploadFile` parameter and calls `ingest_pdf()` synchronously before returning. The ingestion pipeline (`app/services/rag.py`) is already file-path based and reusable per file — no changes needed there. The only change surface is `app/routers/upload.py`.

## Goals / Non-Goals

**Goals:**
- Accept 1–50 PDF files in a single multipart request
- Validate each file independently (PDF type, < 5 MB)
- Ingest each file sequentially using the existing `ingest_pdf()`
- Return a per-file result list (success with chunk count, or failure with error message)
- Overwrite silently on duplicate filenames

**Non-Goals:**
- Async/background ingestion — synchronous is intentional for simplicity
- Parallel ingestion across files — sequential is sufficient
- Persistent job tracking or status polling
- Changes to the ingestion pipeline itself

## Decisions

**`files: list[UploadFile]` via FastAPI form parameter**
FastAPI natively supports `list[UploadFile]` when the client sends multiple fields with the same name (`files`). No middleware or custom parsing needed.

**Best-effort error handling with per-file try/except**
Each file is processed inside an independent `try/except` block. A parse failure or ingestion error on one file is caught, recorded as `{ "filename": ..., "error": ... }`, and processing continues with the next file. The overall response is always HTTP 200 as long as the request itself is valid (correct file count, etc.).

**Batch-level validation returns HTTP 400**
- 0 files: rejected (no-op request)
- > 50 files: rejected (guard against abuse)
These are checked before any file is touched.

**Per-file validation failures included in response, not raised**
If a file fails PDF type or size validation, it's treated the same as an ingestion error — recorded in the response as `{ "filename": ..., "error": "..." }` and processing continues. This is consistent with the best-effort model.

**Response model uses a Union type per entry**
Each entry is either `{ filename, chunks: int }` or `{ filename, error: str }`. Implemented as a Pydantic model with `Optional` fields or a discriminated union.

## Risks / Trade-offs

- **Long request duration**: 50 large PDFs processed synchronously could take minutes. Callers must handle long timeouts. Mitigation: document expected latency; the 5 MB per-file cap bounds worst-case processing time.
- **Memory**: All files are read into memory before saving (current behavior). With 50 files × 5 MB = up to 250 MB peak. Mitigation: acceptable for a course/demo context; production would stream to disk.
- **Breaking change**: Response schema changes from object to list. Existing callers must update. Mitigation: clearly documented in proposal.
