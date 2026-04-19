## Context

Upload handling lives in `app/routers/upload.py`. Each file is read fully into memory, size-checked against `MAX_FILE_SIZE`, then written to disk and passed to `ingest_pdf()`. The batch file count limit (`MAX_FILES = 50`) is unchanged.

## Goals / Non-Goals

**Goals:**

- Set the per-file byte limit to 50 × 1024 × 1024.
- Keep validation semantics: reject when `len(content) > MAX_FILE_SIZE` (so a file of exactly 50 MB is accepted).
- Align error copy and OpenSpec requirements with "50 MB".

**Non-Goals:**

- Streaming uploads or chunked writes to disk.
- Changing `MAX_FILES`, multipart shape, or best-effort per-file error behavior.
- Tuning the ingestion pipeline for very large PDFs beyond updating the gate.

## Decisions

**Single constant `MAX_FILE_SIZE`**

Continue using one module-level constant so the limit is defined once and matches the spec text.

**Inclusive boundary at exactly 50 MB**

Preserve the existing pattern (`>` comparison): exactly at the limit succeeds; one byte over fails.

## Risks / Trade-offs

- **Memory:** Worst-case resident memory for a single request remains "read each file fully." With 50 files × 50 MB, theoretical peak is large; acceptable for this course/demo service but worth noting for operators. Callers sending huge batches may need generous timeouts.
- **Processing time:** Larger PDFs increase synchronous ingestion duration; unchanged architecturally from today, only scaled.
