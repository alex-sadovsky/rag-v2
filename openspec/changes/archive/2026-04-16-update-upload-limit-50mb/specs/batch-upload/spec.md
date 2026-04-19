## MODIFIED Requirements

### Requirement: Accept multiple PDF files in a single upload request

#### Scenario: Successful batch upload

- **WHEN** a client sends `POST /upload` with 3 valid PDF files each under 50 MB
- **THEN** the server responds with HTTP 200 and a JSON array with one entry per file, each containing `filename` and `chunks`
