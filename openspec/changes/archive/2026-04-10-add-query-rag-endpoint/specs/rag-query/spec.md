## ADDED Requirements

### Requirement: Query endpoint retrieves chunks and answers with a grounded model
The application SHALL expose `POST /query` that accepts a JSON body including a user question, retrieves relevant chunks from the in-memory Chroma vector store using the same embedding model as ingestion, and generates a response using Anthropic Claude Haiku 4.5 with instructions to rely only on the retrieved context.

#### Scenario: Successful query returns an answer
- **WHEN** the vector store contains chunks from ingested documents and a valid `ANTHROPIC_API_KEY` is configured
- **AND** a client sends `POST /query` with a question about content present in those chunks
- **THEN** the server responds with HTTP 200 and a body that includes the model’s answer derived from retrieved passages

#### Scenario: API key missing
- **WHEN** `ANTHROPIC_API_KEY` is not configured
- **AND** a client sends `POST /query`
- **THEN** the server responds with an error status and a message indicating configuration is required (the application SHALL NOT silently fail or expose raw provider errors in production-oriented defaults)

### Requirement: Default model is Claude Haiku 4.5
The application SHALL use the Anthropic model id `claude-haiku-4-5` by default for query responses, unless overridden via configuration (e.g. environment variable).

#### Scenario: Model override via environment
- **WHEN** `ANTHROPIC_MODEL` is set to a different allowed model id
- **THEN** query generation uses that model id instead of the default

### Requirement: Grounding behavior
The application SHALL send a system (or equivalent) instruction with each query that requires the model to answer only from the provided retrieved chunk text and to state clearly when the context does not support an answer.

#### Scenario: Irrelevant question to indexed content
- **WHEN** the user question cannot be answered from retrieved chunks
- **THEN** the model response indicates insufficient information in the provided context rather than inventing document-specific facts
