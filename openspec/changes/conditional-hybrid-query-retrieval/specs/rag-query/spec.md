## ADDED Requirements

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
