## MODIFIED Requirements

### Requirement: Upload PDF via POST /upload

#### Scenario: Successful PDF upload

- **WHEN** a client sends `POST /upload` with a valid PDF file under 50 MB
- **THEN** the server responds with HTTP 200 and a JSON array containing one entry with `filename` and `chunks` (e.g., `[{"filename": "document.pdf", "chunks": 12}]`)

### Requirement: Enforce 50 MB file size limit

The endpoint SHALL reject any PDF file whose size exceeds 50 MB (50 × 1024 × 1024 bytes). Per-file size violations SHALL be reported as errors in the response array rather than failing the entire request.

#### Scenario: Upload oversized PDF in a batch

- **WHEN** a client sends `POST /upload` with one valid PDF and one PDF larger than 50 MB
- **THEN** the server responds with HTTP 200, the valid PDF entry contains `chunks`, and the oversized PDF entry contains `error`

#### Scenario: Upload PDF exactly at size limit

- **WHEN** a client sends `POST /upload` with a PDF of exactly 50 MB
- **THEN** the server accepts the file and responds with HTTP 200 with a `chunks` entry
