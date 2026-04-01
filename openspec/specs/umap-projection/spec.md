## ADDED Requirements

### Requirement: Project embeddings to 2D via UMAP
The system SHALL expose a `POST /api/vectors/project` endpoint that accepts a list of high-dimensional embeddings and returns 2D UMAP coordinates along with optional KMeans cluster labels.

#### Scenario: Successful projection
- **WHEN** a valid JSON body with a non-empty `embeddings` array is posted to `/api/vectors/project`
- **THEN** the response SHALL be HTTP 200 with a `coords` array of `[x, y]` pairs, one per input embedding

#### Scenario: Insufficient points for UMAP
- **WHEN** fewer than 2 embeddings are provided
- **THEN** the response SHALL be HTTP 422 with an error message explaining the minimum requirement

### Requirement: Return KMeans cluster labels with projection
The system SHALL accept an optional `n_clusters` parameter (integer, default 8, min 2). When provided, the system SHALL run KMeans on the projected 2D coordinates and include a `cluster_labels` array in the response.

#### Scenario: Clustering requested
- **WHEN** `n_clusters` is included in the request body
- **THEN** the response SHALL include a `cluster_labels` array of integers of equal length to `coords`

#### Scenario: Clustering not requested
- **WHEN** `n_clusters` is absent from the request body
- **THEN** `cluster_labels` SHALL be `null` in the response

### Requirement: Use fixed UMAP hyperparameters
The system SHALL use `n_neighbors=15` and `min_dist=0.1` for UMAP reduction. These SHALL NOT be user-configurable.

#### Scenario: Projection uses fixed parameters
- **WHEN** a projection request is made
- **THEN** UMAP SHALL run with `n_neighbors=15` and `min_dist=0.1` regardless of any extra fields in the request body
