## 1. Configuration

- [x] 1.1 Add `uploads_dir: str = "uploads"` field to `app/config.py` `Settings` class

## 2. Upload Router

- [x] 2.1 Create `app/routers/upload.py` with a `POST /upload` endpoint accepting `UploadFile`
- [x] 2.2 Validate file extension and content type — return HTTP 415 if not PDF
- [x] 2.3 Read file content and enforce 5 MB limit — return HTTP 413 if exceeded
- [x] 2.4 Create `uploads_dir` if it does not exist, then write the file to disk
- [x] 2.5 Return `{"filename": "<original_filename>"}` on success

## 3. Router Registration

- [x] 3.1 Import and include the upload router in `app/routers/__init__.py`

## 4. Verification

- [x] 4.1 Upload a valid PDF under 5 MB — verify HTTP 200 and file appears in `uploads/`
- [x] 4.2 Upload a PDF over 5 MB — verify HTTP 413
- [x] 4.3 Upload a non-PDF file — verify HTTP 415
