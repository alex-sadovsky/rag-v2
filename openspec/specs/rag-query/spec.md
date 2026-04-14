## Requirements

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

### Requirement: Dense-first retrieval for queries
The application SHALL perform **embedding similarity retrieval first** on every `POST /query` request using the same embedding model as ingestion, before any optional lexical retrieval.

#### Scenario: Dense retrieval always runs first
- **WHEN** a client sends `POST /query` with a valid question and the vector store contains chunks
- **THEN** the server SHALL retrieve candidate chunks using dense (vector) search prior to any BM25 step

### Requirement: Conditional BM25 retrieval
The application SHALL run **BM25 (lexical) retrieval** only when **both** conditions hold:

1. **Weak dense signal** — retrieved dense results satisfy configured criteria indicating low confidence (e.g. distance/similarity thresholds on top results).
2. **Lexical warrant** — the question satisfies configured, deterministic rules indicating that term-based matching is likely to help.

When either condition fails, the application SHALL NOT run BM25 for that request.

#### Scenario: BM25 skipped when dense retrieval is strong
- **WHEN** dense retrieval scores indicate confidence above the configured “weak” threshold
- **THEN** the server SHALL NOT invoke BM25 for that query

#### Scenario: BM25 skipped when lexical warrant is false
- **WHEN** dense retrieval is weak but the question does not match lexical warrant rules
- **THEN** the server SHALL NOT invoke BM25 for that query

#### Scenario: BM25 runs only when both gates pass
- **WHEN** dense retrieval is weak and the question matches lexical warrant rules
- **THEN** the server MAY retrieve additional candidates using BM25 and merge them with dense results according to the implemented fusion policy

### Requirement: Fusion preserves dense-first ordering policy
When BM25 retrieval runs, the application SHALL merge BM25 results with dense results using a **documented dense-first policy** (e.g. preserve dense ranking as primary and append or interleave without letting BM25 override dense order arbitrarily), and SHALL cap the final chunk list used for prompting to bounded size consistent with the request’s `k` (or documented fused cap).

#### Scenario: Final context size is bounded
- **WHEN** hybrid fusion runs
- **THEN** the number of chunks passed to the model SHALL NOT exceed the documented maximum derived from `k` and configuration

### Requirement: Hierarchical grounding uses parent page context

When retrieved chunks include hierarchical ingestion metadata, the application SHALL incorporate **both** the child chunk text (dense retrieval unit) **and** the associated **parent page text** from metadata into the prompt context passed to the model, using a consistent labeled format (e.g. excerpt plus full page context), unless configuration disables parent inclusion. When such metadata is absent (e.g. legacy chunks), the application SHALL fall back to using only the chunk’s primary text.

#### Scenario: Child with parent metadata expands the prompt

- **WHEN** a retrieved chunk’s metadata includes non-empty `parent_page_content` and parent inclusion is enabled
- **THEN** the assembled context for that passage includes the child text and the parent page text in the documented structured format

#### Scenario: Legacy chunk without parent metadata

- **WHEN** a retrieved chunk has no `parent_page_content` (or it is empty)
- **THEN** the assembled context uses only the chunk’s main body text as before, without failing the request

#### Scenario: Parent inclusion can be disabled via configuration

- **WHEN** configuration disables parent page text in prompts
- **THEN** the assembled context uses only each chunk’s primary body text even if `parent_page_content` is present
