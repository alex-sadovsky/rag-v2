## MODIFIED Requirements

### Requirement: Upload PDF via POST /upload
The application SHALL expose a `POST /upload` endpoint that accepts a single PDF file via multipart/form-data, saves it to the local uploads directory, runs the RAG ingestion pipeline, and returns the filename and chunk count.

#### Scenario: Successful PDF upload
- **WHEN** a client sends `POST /upload` with a valid PDF file under 5 MB
- **THEN** the server responds with HTTP 200 and a JSON body containing the saved filename and the number of indexed chunks (e.g., `{"filename": "document.pdf", "chunks": 12}`)
