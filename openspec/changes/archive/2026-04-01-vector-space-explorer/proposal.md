## Why

Understanding what's stored in a vector database is currently opaque — there's no way to visually inspect embedding quality, cluster structure, or neighbor relationships without writing custom scripts. An interactive visualization tool makes the RAG pipeline's semantic space explorable and debuggable.

## What Changes

- New API endpoint to export vectors and metadata from ChromaDB
- New API endpoint to run UMAP dimensionality reduction on the exported embeddings
- New API endpoint to find nearest neighbors for a query string
- New frontend visualization page using Plotly with interactive scatter plot
- Points colored by metadata field or auto-detected cluster (KMeans)
- Click-to-select query highlights its k-nearest neighbors

## Capabilities

### New Capabilities

- `vector-export`: Export document vectors and metadata from ChromaDB collections
- `umap-projection`: Reduce high-dimensional embeddings to 2D using UMAP for visualization
- `vector-visualization`: Interactive Plotly scatter plot with metadata coloring and cluster support
- `neighbor-highlight`: Embed a query string and highlight its k-nearest neighbors in the visualization

### Modified Capabilities

## Impact

- **New dependencies**: `umap-learn`, `plotly`, `scikit-learn` (KMeans clustering)
- **New API routes**: `GET /api/vectors/export`, `POST /api/vectors/project`, `POST /api/vectors/neighbors`
- **New frontend page**: `/visualize` served as a static HTML + JS page via FastAPI
- **Affected systems**: ChromaDB vector store (read-only access), embedding model (reused for query encoding)
