## Requirements

### Requirement: Accept multiple PDF files in a single upload request
The `POST /upload` endpoint SHALL accept between 1 and 50 PDF files in a single multipart/form-data request using a repeated `files` field. It SHALL process each file independently and return a list of per-file results.

#### Scenario: Successful batch upload
- **WHEN** a client sends `POST /upload` with 3 valid PDF files each under 5 MB
- **THEN** the server responds with HTTP 200 and a JSON array with one entry per file, each containing `filename` and `chunks`

#### Scenario: Single file still works
- **WHEN** a client sends `POST /upload` with exactly 1 valid PDF file
- **THEN** the server responds with HTTP 200 and a JSON array with one entry containing `filename` and `chunks`

### Requirement: Enforce batch size limits
The endpoint SHALL reject requests with 0 files or more than 50 files with HTTP 400.

#### Scenario: No files submitted
- **WHEN** a client sends `POST /upload` with no files
- **THEN** the server responds with HTTP 400 and an error message

#### Scenario: Too many files submitted
- **WHEN** a client sends `POST /upload` with 51 or more files
- **THEN** the server responds with HTTP 400 and an error message

### Requirement: Best-effort ingestion with per-file error reporting
If one file in the batch fails validation or ingestion, the endpoint SHALL continue processing remaining files. The failed file SHALL be represented in the response with a `filename` and `error` field instead of `chunks`.

#### Scenario: One file fails, others succeed
- **WHEN** a client sends `POST /upload` with 3 files and the second file is corrupt
- **THEN** the server responds with HTTP 200 and a JSON array where the first and third entries contain `chunks` and the second entry contains `error`

#### Scenario: All files fail
- **WHEN** a client sends `POST /upload` with 2 files that both fail ingestion
- **THEN** the server responds with HTTP 200 and a JSON array where both entries contain `error`

### Requirement: Duplicate filenames are silently overwritten
If a file in the batch has the same name as an already-saved file, the endpoint SHALL overwrite the existing file without error.

#### Scenario: Re-uploading an existing filename
- **WHEN** a client uploads a file named `report.pdf` that already exists in the uploads directory
- **THEN** the file is overwritten and the response contains `filename: "report.pdf"` with updated `chunks`
