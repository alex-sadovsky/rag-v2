## ADDED Requirements

### Requirement: PDF is ingested into vector store after upload
After a PDF is saved to disk, the application SHALL parse it, split it into chunks of 1000 characters, embed each chunk using `all-MiniLM-L6-v2`, and add the chunks to the in-memory Chroma vector store.

#### Scenario: Successful ingestion returns chunk count
- **WHEN** a valid PDF is uploaded
- **THEN** the upload response includes a `chunks` field with the number of chunks indexed (e.g., `{"filename": "doc.pdf", "chunks": 12}`)

#### Scenario: Multi-page PDF is fully indexed
- **WHEN** a PDF with multiple pages is uploaded
- **THEN** all pages are parsed and all resulting chunks are added to the vector store

### Requirement: Vector store is a shared in-memory singleton
The application SHALL maintain a single Chroma vector store instance for its lifetime. All uploaded PDFs are added to the same store and the store resets when the application restarts.

#### Scenario: Second upload adds to existing store
- **WHEN** two PDFs are uploaded in sequence
- **THEN** both documents' chunks are present in the vector store

### Requirement: Embeddings use all-MiniLM-L6-v2
The application SHALL use `HuggingFaceEmbeddings` with model `sentence-transformers/all-MiniLM-L6-v2` to generate all chunk embeddings.

#### Scenario: Embedding model is consistent across uploads
- **WHEN** multiple PDFs are uploaded in the same session
- **THEN** all chunks are embedded with the same model instance
