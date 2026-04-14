## ADDED Requirements

### Requirement: Hierarchical grounding uses parent page context

When retrieved chunks include hierarchical ingestion metadata, the application SHALL incorporate **both** the child chunk text (dense retrieval unit) **and** the associated **parent page text** from metadata into the prompt context passed to the model, using a consistent labeled format (e.g. excerpt plus full page context). When such metadata is absent (e.g. legacy chunks), the application SHALL fall back to using only the chunk’s primary text.

#### Scenario: Child with parent metadata expands the prompt

- **WHEN** a retrieved chunk’s metadata includes non-empty `parent_page_content`
- **THEN** the assembled context for that passage includes the child text and the parent page text in the documented structured format

#### Scenario: Legacy chunk without parent metadata

- **WHEN** a retrieved chunk has no `parent_page_content` (or it is empty)
- **THEN** the assembled context uses only the chunk’s main body text as today, without failing the request
