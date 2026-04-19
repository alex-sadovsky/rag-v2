# RAG v2

A FastAPI application that ingests PDF documents into a vector store, answers questions with **retrieval-augmented generation** (Chroma + Claude Haiku), and provides interactive embedding visualization.

The sample dataset link:
https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset

It has been chosen as resumes is well-known domain, which does not require special knowledge and allows quicker check the RAG quality, create golden dataset.

## Setup

**Requirements:** Python 3.11+

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The app imports the **`mcp_csv_server`** package from `mcp_csv_server_pkg/` (same code as the stdio MCP server). Installing via **`requirements.txt`** ensures that local package is installed before the FastAPI app. Alternatively: `pip install -e ./mcp_csv_server_pkg` then `pip install -e .`.

For tests and dev tools, use **`pip install -r requirements-dev.txt`** instead of **`requirements.txt`**.

### Optional configuration

Create a `.env` file to override defaults:

```env
APP_TITLE=My RAG App
HOST=127.0.0.1
PORT=8000
UPLOADS_DIR=uploads
```

### Anthropic API (RAG query)

For most questions, `POST /query` retrieves chunks from the vector store and calls the Anthropic API to generate an answer. If the question clearly targets **global natural-disaster records** (EM-DAT–style data in `dataset/csv/`), the app answers using the **same tabular query logic** as the MCP tool `query_natural_disasters`—**no LLM call** and **no** `ANTHROPIC_API_KEY` required for that branch.

Configure credentials with environment variables (or entries in `.env`):

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | **Yes**, for RAG `/query` | API key from the [Anthropic Console](https://console.anthropic.com/). If unset, `/query` responds with **503** for normal document questions; natural-disaster CSV queries still work when routed. |
| `ANTHROPIC_MODEL` | No | Model id for generation. Default: `claude-haiku-4-5`. Override if you need another Claude model. |
| `QUERY_DENSE_WEAK_BEST_DISTANCE_GT` | No | Dense retrieval “weak” gate: if the best Chroma distance is **above** this value, dense matches are considered weak (lower distance = closer match). Default `1.5` (conservative). Tune with your data. |
| `QUERY_LEXICAL_MIN_ALPHA_TOKENS` | No | Minimum content-word count (after a small English stopword list) before the lexical warrant can pass via the “enough tokens” rule. Default `5`. |
| `QUERY_LEXICAL_ENABLE_QUOTES` | No | If `true` (default), double- or single-quoted spans in the question satisfy lexical warrant. |
| `QUERY_LEXICAL_ENABLE_IDENTIFIERS` | No | If `true` (default), digits, hyphenated tokens, CamelCase, or ALL-CAPS tokens can satisfy lexical warrant. |

Example:

```env
ANTHROPIC_API_KEY=sk-ant-api03-...
# Optional:
# ANTHROPIC_MODEL=claude-haiku-4-5
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

**Limits:** up to 50 files per request, max 50 MB each.

```bash
curl -X POST http://localhost:8000/upload \
  -F "files=@document.pdf"
```

**Response:**
```json
[{"filename": "document.pdf", "chunks": 12}]
```

### RAG query (`POST /query`)

Asks a natural-language question using chunks already in the vector store. Retrieval is **dense-first**: every request runs embedding similarity in Chroma (same model as ingestion). **BM25 (lexical) search runs only when** dense hits look weak (best distance above a configurable threshold) **and** a small deterministic **lexical warrant** matches (for example quoted phrases, identifiers, or enough content words). When both gates pass, BM25 candidates are merged **dense-first** (dense order preserved; extra BM25 hits appended without exceeding `k`). Then passages are sent to **Claude Haiku 4.5** with a grounding prompt so the model answers only from the provided context.

**Prerequisites:** Upload at least one PDF via `POST /upload` in the same app session (the store is in-memory). Set `ANTHROPIC_API_KEY` as described above.

**Browser UI:** While the server is running, open **`/chat`** (e.g. `http://127.0.0.1:8000/chat`) for a simple page that calls the same `POST /query` API and shows answers and sources.

```
POST /query
Content-Type: application/json
```

**Request body (JSON)**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `question` | string | — | Required. Non-empty after trimming. User question; embedded and matched against indexed chunks. |
| `k` | integer | `5` | How many chunks to retrieve (`1`–`20`). |

**Response body (JSON)**

| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | Model answer grounded on retrieved passages (or a short message if nothing is indexed or no chunks were retrieved). |
| `sources` | array | Retrieved chunks: each item has `content` (chunk text) and `metadata` (e.g. page info from LangChain). |

**Example**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of the document?", "k": 5}'
```

**Example response**

```json
{
  "answer": "According to the provided passages, ...",
  "sources": [
    {
      "content": "First chunk text ...",
      "metadata": {"page": 1, "source": "document.pdf"}
    }
  ]
}
```

**Errors**

- **503** — `ANTHROPIC_API_KEY` is not configured.
- **422** — Invalid body (e.g. empty `question`, or `k` outside `1`–`20`).

OpenAPI details: `/docs` → **RAG query over indexed PDFs**.

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

### Resume analytics (`GET /api/resumes/analytics`)

Returns **aggregates derived from plain text** extracted from PDF files on disk under `UPLOADS_DIR` (default `uploads/`). This endpoint does **not** use embeddings, Chroma, or vector coordinates — only the same PDF text path as ingestion (`PyPDFLoader`).

**Query parameters**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `top_skills` | `15` | Maximum number of skills in the response (`1`–`200`). |
| `include_other` | `true` | If `false`, the `Other` section category is omitted from the pie chart data. |

**Response (JSON)**

| Field | Description |
|-------|-------------|
| `files_scanned` | Number of PDFs successfully read. |
| `categories` | Pie data: `id`, human `label`, and `count` (characters attributed to each detected resume section). |
| `skills` | Top skills after lexicon matching; each skill counts **at most once per PDF** (`skill_match_mode`: `per_file_dedupe`), then totals across files. |
| `warnings` | Optional messages (e.g. unreadable files). |
| `skill_match_mode` | Always `per_file_dedupe` in this version — documents the counting rule. |

**Example**

```bash
curl -s "http://localhost:8000/api/resumes/analytics?top_skills=20&include_other=true"
```

**Example response (abridged)**

```json
{
  "files_scanned": 2,
  "categories": [
    { "id": "experience", "label": "Experience", "count": 4200 },
    { "id": "education", "label": "Education", "count": 800 }
  ],
  "skills": [
    { "skill": "Python", "count": 2 },
    { "skill": "SQL", "count": 1 }
  ],
  "warnings": [],
  "skill_match_mode": "per_file_dedupe"
}
```

Editable skill list: `app/data/skills_lexicon.txt` (longer phrases should appear before shorter ones in the file; the service deduplicates and sorts by length when matching).

**Browser:** open `http://localhost:8000/analytics` for Plotly **pie** (section shares) and **horizontal bar** (skills) charts loaded from this API.

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

## Resume analytics (PDF text)

Open:

```
http://localhost:8000/analytics
```

After uploading PDFs with `POST /upload`, this page fetches `GET /api/resumes/analytics` and shows:

- **Section categories** — heuristic mapping of headings (Experience, Education, Skills, etc.) to character counts in each bucket.
- **Skills** — substring matches against `app/data/skills_lexicon.txt`, one hit per skill per file, then aggregated.

This view is independent of the embedding / UMAP visualization at `/visualize`.
