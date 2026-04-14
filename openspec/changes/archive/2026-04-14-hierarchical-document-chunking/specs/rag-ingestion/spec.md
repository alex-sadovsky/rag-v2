## MODIFIED Requirements

### Requirement: PDF is ingested into vector store after upload

After a PDF is saved to disk, the application SHALL parse it, **treat each page as a parent scope**, split each page into **child** chunks using configured target size and overlap (replacing a single global flat split), embed each **child** using `all-MiniLM-L6-v2`, and add those child chunks to the in-memory Chroma vector store. Each child chunk SHALL include metadata with at least: document `source`, `page` index, **`child_index`** (position within that page), and **`parent_page_content`** containing the full text of the parent page before child splitting.

#### Scenario: Successful ingestion returns chunk count

- **WHEN** a valid PDF is uploaded
- **THEN** the upload response includes a `chunks` field with the number of **child** chunks indexed (e.g., `{"filename": "doc.pdf", "chunks": 12}`)

#### Scenario: Multi-page PDF is fully indexed

- **WHEN** a PDF with multiple pages is uploaded
- **THEN** all pages are parsed and all resulting **child** chunks are added to the vector store

#### Scenario: Child chunks preserve page hierarchy

- **WHEN** a page produces multiple child chunks
- **THEN** each child’s metadata includes the same `page` value as its parent page and a `child_index` ordering within that page

#### Scenario: Parent page text is available on every child

- **WHEN** any child chunk is stored
- **THEN** its metadata includes `parent_page_content` equal to the full parent page text for that `page`

### Requirement: Vector store is a shared in-memory singleton

No change to behavior — the application SHALL maintain a single Chroma vector store instance for its lifetime. All uploaded PDFs are added to the same store and the store resets when the application restarts.

### Requirement: Embeddings use all-MiniLM-L6-v2

No change to behavior — the application SHALL use `HuggingFaceEmbeddings` with model `sentence-transformers/all-MiniLM-L6-v2` to generate all **child** chunk embeddings.
