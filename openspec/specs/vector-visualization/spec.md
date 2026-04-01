## ADDED Requirements

### Requirement: Serve interactive visualization page
The system SHALL serve a self-contained HTML page at `GET /visualize` that renders an interactive Plotly scatter plot of the projected embedding space.

#### Scenario: Page loads successfully
- **WHEN** a browser requests `GET /visualize`
- **THEN** the response SHALL be HTTP 200 with `Content-Type: text/html` and a valid HTML page containing a Plotly scatter plot

#### Scenario: Empty collection state
- **WHEN** the page loads and the export API returns an empty collection
- **THEN** the page SHALL display a clear message: "No documents ingested yet. Upload PDFs first."

### Requirement: Color points by metadata field
The page SHALL allow the user to select a metadata field from a dropdown and color each scatter point by that field's value. If the field has string values, distinct colors SHALL be assigned per unique value.

#### Scenario: User selects source metadata field
- **WHEN** the user selects "source" from the color-by dropdown
- **THEN** each point SHALL be recolored by its source filename with a legend showing the mapping

### Requirement: Color points by cluster label
The page SHALL provide a "Cluster" option in the color-by dropdown that colors points by their KMeans cluster assignment.

#### Scenario: User selects cluster coloring
- **WHEN** the user selects "Cluster" from the color-by dropdown
- **THEN** each point SHALL be colored by its integer cluster label with a legend

### Requirement: Show document text on hover
Each scatter point SHALL display a tooltip on hover showing the document chunk text (truncated to 200 characters) and all metadata key-value pairs.

#### Scenario: User hovers over a point
- **WHEN** the user hovers over a scatter point
- **THEN** a tooltip SHALL appear with the chunk text and metadata
