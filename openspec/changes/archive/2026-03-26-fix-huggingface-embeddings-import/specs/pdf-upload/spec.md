## ADDED Requirements

### Requirement: Embeddings ingestion SHALL not emit deprecation warnings
The PDF ingestion pipeline SHALL use a non-deprecated embeddings integration. No `LangChainDeprecationWarning` SHALL be raised when `HuggingFaceEmbeddings` is instantiated during PDF processing.

#### Scenario: Upload triggers no LangChain deprecation warning
- **WHEN** a valid PDF is uploaded via `POST /upload`
- **THEN** no `LangChainDeprecationWarning` is emitted by the embeddings layer
