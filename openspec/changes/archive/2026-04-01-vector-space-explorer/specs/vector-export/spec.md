## ADDED Requirements

### Requirement: Export vectors and metadata from ChromaDB
The system SHALL expose a `GET /api/vectors/export` endpoint that retrieves all document embeddings, metadata, and document text from the default ChromaDB collection.

#### Scenario: Successful export with documents
- **WHEN** the collection contains at least one document and a `GET /api/vectors/export` request is made
- **THEN** the response SHALL be HTTP 200 with a JSON body containing arrays of `ids`, `embeddings`, `documents`, and `metadatas` with equal length

#### Scenario: Export with empty collection
- **WHEN** no documents have been ingested and a `GET /api/vectors/export` request is made
- **THEN** the response SHALL be HTTP 200 with empty arrays and a `"warning"` field set to `"Collection is empty"`

### Requirement: Cap exported points to prevent performance issues
The system SHALL accept an optional `max_points` query parameter (integer, default 5000). When the collection has more documents than `max_points`, the system SHALL return a random sample of that size and include a `"sampled": true` flag in the response.

#### Scenario: Collection exceeds max_points
- **WHEN** the collection has more documents than `max_points` and export is requested
- **THEN** the response SHALL contain exactly `max_points` items (randomly sampled) and `"sampled": true`

#### Scenario: Collection within max_points
- **WHEN** the collection has fewer or equal documents than `max_points`
- **THEN** the response SHALL contain all documents and `"sampled": false`
