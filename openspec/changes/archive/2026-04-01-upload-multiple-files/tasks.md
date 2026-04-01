## 1. Response Models

- [x] 1.1 Add `UploadFileResult` Pydantic model with `filename: str` and optional `chunks: int | None` and `error: str | None`

## 2. Endpoint Refactor

- [x] 2.1 Change `file: UploadFile` parameter to `files: list[UploadFile]` in `upload_pdf()`
- [x] 2.2 Add batch-level validation: return HTTP 400 if `len(files) == 0` or `len(files) > 50`
- [x] 2.3 Move per-file validation (PDF type, 5 MB limit) inside a loop with try/except, recording errors instead of raising
- [x] 2.4 Move file save + `ingest_pdf()` call inside the same try/except, appending result to output list
- [x] 2.5 Update return type to `list[UploadFileResult]`

## 3. Verification

- [x] 3.1 Test batch upload with multiple valid PDFs — verify response is a list with `chunks` per file
- [x] 3.2 Test with one invalid file in batch — verify other files succeed and invalid file has `error`
- [x] 3.3 Test with 0 files — verify HTTP 400
- [x] 3.4 Test with 51 files — verify HTTP 400
- [x] 3.5 Test re-upload of same filename — verify file is overwritten and response contains updated `chunks`
