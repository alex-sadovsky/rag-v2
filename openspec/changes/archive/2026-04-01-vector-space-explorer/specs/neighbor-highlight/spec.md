## ADDED Requirements

### Requirement: Find nearest neighbors for a query string
The system SHALL expose a `POST /api/vectors/neighbors` endpoint that accepts a query string and `k` value, embeds the query using the same model as ingestion, and returns the IDs and distances of the k nearest neighbors in the collection.

#### Scenario: Successful neighbor search
- **WHEN** a valid JSON body with `query` (non-empty string) and `k` (positive integer) is posted to `/api/vectors/neighbors`
- **THEN** the response SHALL be HTTP 200 with a `neighbor_ids` array of document IDs and a `distances` array of floats, each of length `k`

#### Scenario: k exceeds collection size
- **WHEN** `k` is greater than the number of documents in the collection
- **THEN** the response SHALL return all available documents and set `k_actual` to the actual count returned

#### Scenario: Empty query string
- **WHEN** the `query` field is an empty string
- **THEN** the response SHALL be HTTP 422 with a validation error

### Requirement: Highlight nearest neighbors in the visualization
The visualization page SHALL include a query input and "Find Neighbors" button. After submitting, the k nearest neighbor points SHALL be visually highlighted (larger marker, distinct outline) while all other points are dimmed.

#### Scenario: User submits a query
- **WHEN** the user types a query and clicks "Find Neighbors"
- **THEN** the k nearest neighbor points SHALL be highlighted with a larger marker size and red outline, and all other points SHALL be dimmed to 30% opacity

#### Scenario: User clears the query
- **WHEN** the user clears the query input and clicks "Reset"
- **THEN** all points SHALL return to their original color and opacity
