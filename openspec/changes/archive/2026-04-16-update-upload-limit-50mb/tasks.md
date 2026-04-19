## 1. Implementation

- [x] 1.1 Set `MAX_FILE_SIZE` to `50 * 1024 * 1024` in `app/routers/upload.py` and update the `ValueError` message to reference 50 MB.
- [x] 1.2 Update `README.md` limits line if it still says 5 MB per file.

## 2. Specs (when applying the change to canonical specs)

- [x] 2.1 Update `openspec/specs/pdf-upload/spec.md`: all 5 MB references → 50 MB, including requirement title, byte formula, and scenarios.
- [x] 2.2 Update `openspec/specs/batch-upload/spec.md`: scenario text that says "under 5 MB" → "under 50 MB".

## 3. Verification

- [x] 3.1 Manually or with a test: upload a PDF under 50 MB — success path unchanged.
- [x] 3.2 Confirm a file just over 50 MB is rejected with the per-file error in the response array (same behavior as today, new threshold).
