## MODIFIED Requirements

### Requirement: Upload PDF via POST /upload
The application SHALL expose a `POST /upload` endpoint that accepts 1 to 50 PDF files via multipart/form-data (repeated `files` field), saves each to the local uploads directory, runs the RAG ingestion pipeline per file, and returns a JSON array of per-file results containing the filename and either the chunk count (on success) or an error message (on failure).

#### Scenario: Successful PDF upload
- **WHEN** a client sends `POST /upload` with a valid PDF file under 5 MB
- **THEN** the server responds with HTTP 200 and a JSON array containing one entry with `filename` and `chunks` (e.g., `[{"filename": "document.pdf", "chunks": 12}]`)

### Requirement: Reject non-PDF files
The endpoint SHALL reject any uploaded file whose content type is not `application/pdf` or whose filename does not end with `.pdf`. Per-file rejections SHALL be reported as errors in the response array rather than failing the entire request.

#### Scenario: Upload a non-PDF file in a batch
- **WHEN** a client sends `POST /upload` with one PDF and one PNG file
- **THEN** the server responds with HTTP 200, the PDF entry contains `chunks`, and the PNG entry contains `error` indicating unsupported type

### Requirement: Enforce 5 MB file size limit
The endpoint SHALL reject any PDF file whose size exceeds 5 MB (5 × 1024 × 1024 bytes). Per-file size violations SHALL be reported as errors in the response array rather than failing the entire request.

#### Scenario: Upload oversized PDF in a batch
- **WHEN** a client sends `POST /upload` with one valid PDF and one PDF larger than 5 MB
- **THEN** the server responds with HTTP 200, the valid PDF entry contains `chunks`, and the oversized PDF entry contains `error`

#### Scenario: Upload PDF exactly at size limit
- **WHEN** a client sends `POST /upload` with a PDF of exactly 5 MB
- **THEN** the server accepts the file and responds with HTTP 200 with a `chunks` entry

### Requirement: Save file to local uploads directory
The application SHALL save accepted PDF files to a configurable local directory (default: `uploads/`). The directory SHALL be created automatically if it does not exist.

#### Scenario: Uploads directory is created on first use
- **WHEN** the `uploads/` directory does not exist and a valid PDF is uploaded
- **THEN** the directory is created and the file is saved successfully

### Requirement: Embeddings ingestion SHALL not emit deprecation warnings
The PDF ingestion pipeline SHALL use a non-deprecated embeddings integration. No `LangChainDeprecationWarning` SHALL be raised when `HuggingFaceEmbeddings` is instantiated during PDF processing.

#### Scenario: Upload triggers no LangChain deprecation warning
- **WHEN** a valid PDF is uploaded via `POST /upload`
- **THEN** no `LangChainDeprecationWarning` is emitted by the embeddings layer
