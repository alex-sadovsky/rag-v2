## ADDED Requirements

### Requirement: Upload PDF via POST /upload
The application SHALL expose a `POST /upload` endpoint that accepts a single PDF file via multipart/form-data and saves it to the local uploads directory.

#### Scenario: Successful PDF upload
- **WHEN** a client sends `POST /upload` with a valid PDF file under 5 MB
- **THEN** the server responds with HTTP 200 and a JSON body containing the saved filename (e.g., `{"filename": "document.pdf"}`)

### Requirement: Reject non-PDF files
The endpoint SHALL reject any uploaded file whose content type is not `application/pdf` or whose filename does not end with `.pdf`.

#### Scenario: Upload a non-PDF file
- **WHEN** a client sends `POST /upload` with a file of type `image/png` or extension `.png`
- **THEN** the server responds with HTTP 415 and an error message

### Requirement: Enforce 5 MB file size limit
The endpoint SHALL reject any PDF file whose size exceeds 5 MB (5 × 1024 × 1024 bytes).

#### Scenario: Upload oversized PDF
- **WHEN** a client sends `POST /upload` with a PDF larger than 5 MB
- **THEN** the server responds with HTTP 413 and an error message

#### Scenario: Upload PDF exactly at size limit
- **WHEN** a client sends `POST /upload` with a PDF of exactly 5 MB
- **THEN** the server accepts the file and responds with HTTP 200

### Requirement: Save file to local uploads directory
The application SHALL save accepted PDF files to a configurable local directory (default: `uploads/`). The directory SHALL be created automatically if it does not exist.

#### Scenario: Uploads directory is created on first use
- **WHEN** the `uploads/` directory does not exist and a valid PDF is uploaded
- **THEN** the directory is created and the file is saved successfully
