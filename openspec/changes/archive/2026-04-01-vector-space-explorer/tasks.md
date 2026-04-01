## 1. Dependencies & Configuration

- [x] 1.1 Add `umap-learn>=0.5.0` to `pyproject.toml` dependencies
- [x] 1.2 Create `app/static/` directory for serving the visualization HTML
- [x] 1.3 Mount `StaticFiles` at `/static` and add `GET /visualize` route in `app/main.py`

## 2. Vector Export Service

- [x] 2.1 Create `app/services/vectors.py` with `export_vectors(max_points)` function that calls `vectorstore._collection.get(include=["embeddings", "documents", "metadatas"])` and applies random sampling when needed
- [x] 2.2 Add `ProjectionRequest` and `ProjectionResponse` Pydantic models (embeddings, n_clusters, coords, cluster_labels)
- [x] 2.3 Add `project_embeddings(embeddings, n_clusters)` function in `vectors.py` using `umap-learn` with fixed `n_neighbors=15`, `min_dist=0.1`, plus optional KMeans clustering
- [x] 2.4 Add `NeighborRequest` and `NeighborResponse` Pydantic models (query, k, neighbor_ids, distances, k_actual)
- [x] 2.5 Add `find_neighbors(query, k)` function in `vectors.py` that embeds the query string and queries ChromaDB for k-NN

## 3. Vector API Router

- [x] 3.1 Create `app/routers/vectors.py` with `GET /api/vectors/export` endpoint (accepts `max_points` query param, returns export result with `sampled` flag and optional `warning`)
- [x] 3.2 Add `POST /api/vectors/project` endpoint to `vectors.py` router (validates min 2 embeddings, returns coords + cluster_labels)
- [x] 3.3 Add `POST /api/vectors/neighbors` endpoint to `vectors.py` router (validates non-empty query, handles k > collection size)
- [x] 3.4 Register `vectors_router` in `app/routers/__init__.py`

## 4. Frontend Visualization Page

- [x] 4.1 Create `app/static/visualize.html` with Plotly loaded from CDN and layout: scatter plot area + controls sidebar
- [x] 4.2 Implement JS `loadVisualization()` that calls `/api/vectors/export` then `/api/vectors/project` and renders the Plotly scatter with hover text (chunk text truncated to 200 chars + metadata)
- [x] 4.3 Implement color-by dropdown: populate with detected metadata keys + "Cluster" option, re-color trace on change
- [x] 4.4 Implement empty-state message when export returns zero documents
- [x] 4.5 Implement query input + "Find Neighbors" button that calls `/api/vectors/neighbors`, highlights returned IDs with larger marker + red outline, dims others to 30% opacity
- [x] 4.6 Implement "Reset" button that restores original marker sizes and opacity

## 5. Verification

- [x] 5.1 Ingest at least one PDF via `POST /upload`, then verify `GET /api/vectors/export` returns non-empty arrays
- [x] 5.2 Verify `POST /api/vectors/project` returns `coords` of correct length and `cluster_labels` when `n_clusters` is provided
- [x] 5.3 Verify `POST /api/vectors/neighbors` returns correct number of IDs and distances
- [x] 5.4 Open `/visualize` in a browser, confirm scatter plot renders, color-by dropdown works, and neighbor highlight works for a sample query
