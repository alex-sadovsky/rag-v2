# RAG v2

A FastAPI application that ingests PDF documents into a vector store and provides semantic search and interactive embedding visualization.

## Setup

**Requirements:** Python 3.11+

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e .
```

### Optional configuration

Create a `.env` file to override defaults:

```env
APP_TITLE=My RAG App
HOST=127.0.0.1
PORT=8000
UPLOADS_DIR=uploads
```

## Running the app

```bash
.venv/bin/python main.py
```

The API is available at `http://127.0.0.1:8000`.
Interactive docs: `http://127.0.0.1:8000/docs`

> **Note:** The vector store is in-memory. All ingested documents are lost when the app restarts.

## API

### Health check

```
GET /health
```

### Upload PDFs

Ingests one or more PDF files into the vector store.

```
POST /upload
Content-Type: multipart/form-data
```

**Limits:** up to 50 files per request, max 5 MB each.

```bash
curl -X POST http://localhost:8000/upload \
  -F "files=@document.pdf"
```

**Response:**
```json
[{"filename": "document.pdf", "chunks": 12}]
```

### Export vectors

Returns all stored embeddings, document chunks, and metadata.

```
GET /api/vectors/export?max_points=5000
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_points` | `5000` | Maximum points to return; randomly sampled if exceeded |

### Project to 2D

Reduces embeddings to 2D with UMAP and optionally assigns KMeans cluster labels.

```
POST /api/vectors/project
Content-Type: application/json
```

```json
{"embeddings": [[...], [...]], "n_clusters": 8}
```

### Find nearest neighbors

Embeds a query string and returns the k nearest document chunks.

```
POST /api/vectors/neighbors
Content-Type: application/json
```

```json
{"query": "what is retrieval augmented generation?", "k": 5}
```

## Vector Space Explorer

An interactive visualization of the embedding space is available at:

```
http://localhost:8000/visualize
```

Upload PDFs first, then open the page. It will:

1. Export all vectors from the store
2. Project them to 2D via UMAP
3. Display an interactive Plotly scatter plot

**Controls:**

- **Max points / KMeans clusters** — tune dataset size and cluster count, then click **Load & Project**
- **Color by** — color points by cluster or any metadata field (e.g. `source` filename)
- **Hover** — see the document chunk text and metadata for any point
- **Find Neighbors** — type a query and click the button to highlight the k nearest neighbors in red; all other points are dimmed
- **Reset** — clear the highlight and restore original colors

> Requires an internet connection — Plotly is loaded from CDN.
