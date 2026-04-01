## Context

The app currently has a RAG pipeline that ingests PDFs into a ChromaDB in-memory vector store using `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional embeddings). There is no way to inspect what's stored — the semantic space is completely opaque. This design adds a backend API for vector export + UMAP projection and a self-contained frontend visualization page.

Key constraints:
- ChromaDB is **in-memory** (no persistence between restarts — data must be ingested before visualizing)
- Embeddings are 384-dim; UMAP reduction to 2D is feasible even for thousands of points
- No existing static file serving — must be added

## Goals / Non-Goals

**Goals:**
- Export all vectors + metadata from ChromaDB via REST API
- Project embeddings to 2D via UMAP (server-side)
- Find k-nearest neighbors for an arbitrary query string (server-side embedding)
- Serve a single-page interactive Plotly visualization from FastAPI
- Color points by a chosen metadata field or auto-assigned KMeans cluster label

**Non-Goals:**
- Persistent storage or cross-session state
- Multi-collection support (single default collection only)
- Authentication or access control
- Real-time updates as new documents are ingested
- 3D visualization

## Decisions

### 1. Server-side UMAP vs. client-side

**Decision**: UMAP runs server-side in Python.

Alternatives: run UMAP in the browser via WASM (umap-js). Rejected because the Python `umap-learn` library is more mature, already in the Python environment, and avoids shipping a large JS bundle.

### 2. Single HTML page served by FastAPI vs. separate frontend

**Decision**: Single self-contained HTML file served via `StaticFiles` mount at `/static`, with the visualization page at `GET /visualize` (returns the HTML file via `FileResponse`).

This keeps the change self-contained with no build tooling. Plotly is loaded from CDN.

### 3. API surface

Three new endpoints under `/api/vectors`:

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/vectors/export` | Return all vectors + metadata from ChromaDB |
| `POST` | `/api/vectors/project` | Accept raw embeddings, return UMAP 2D coords |
| `POST` | `/api/vectors/neighbors` | Embed a query, return k-NN doc IDs + distances |

The frontend calls these sequentially: export → project → render, then optionally neighbors on query submit.

**Rationale for split**: Keeps projection stateless and reusable. Export and project are separate so the client holds the 2D coords and can re-query neighbors without re-projecting.

### 4. Clustering

**Decision**: Optional KMeans clustering (scikit-learn) with configurable `n_clusters` (default 8). Cluster labels returned as metadata alongside UMAP coords. User can toggle between coloring by cluster or by a metadata field (e.g., `source` filename).

### 5. Accessing ChromaDB internals

`get_vectorstore()` returns a LangChain `Chroma` wrapper. To get raw vectors we use `vectorstore._collection.get(include=["embeddings", "documents", "metadatas"])` — direct access to the underlying ChromaDB collection object.

**Risk**: This is a private API (`_collection`). Alternative is to use `chromadb.Client` directly, but since `get_vectorstore()` already owns the collection, accessing `_collection` avoids duplicating initialization logic.

## Risks / Trade-offs

- **In-memory store is empty on startup** → Visualization will show an empty plot until documents are ingested. Mitigation: show a clear empty-state message in the UI.
- **`_collection` is a private attribute** → Could break on ChromaDB upgrades. Mitigation: pin ChromaDB version; add a compatibility check in the export service.
- **UMAP is slow for large corpora** → UMAP on ~10k points takes ~5-10s. Mitigation: add a configurable `max_points` cap (default 5000) with random sampling; return a warning in the response.
- **No auth** → Vector contents are exposed to anyone who can reach the API. Acceptable for a local dev/course tool; document the limitation.
- **CDN dependency** → Plotly loaded from CDN; won't work offline. Mitigation: acceptable for course context; document it.

## Migration Plan

1. Add `umap-learn` and `scikit-learn` (already present as sentence-transformers dep) to `pyproject.toml`
2. Add new `VectorService` in `app/services/vectors.py`
3. Add new router `app/routers/vectors.py` with the three endpoints
4. Register router in `app/routers/__init__.py`
5. Mount `StaticFiles` and add `/visualize` route in `app/main.py`
6. Create `app/static/visualize.html`

No data migrations needed (in-memory store). No breaking changes to existing endpoints.

**Rollback**: revert the new files and router registration — zero impact on existing upload/health endpoints.

## Open Questions

- Should UMAP parameters (`n_neighbors`, `min_dist`) be user-configurable via query params, or fixed? (Suggest fixed defaults for now: `n_neighbors=15`, `min_dist=0.1`) - suggest default
- Should the visualization auto-refresh after a new upload, or require manual reload? (Suggest manual for simplicity) - manual
