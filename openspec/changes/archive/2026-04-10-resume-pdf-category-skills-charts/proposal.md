## Why

The app can visualize embedding space (`/visualize`) and answer RAG queries, but there is no aggregate view of **what is actually written** in uploaded resumes. Stakeholders want quick insight into **how resume content is distributed by section/category** and **which skills appear most often**. Those insights must reflect **extracted PDF text**, not geometric properties of embedding vectors (which are useful for similarity but do not directly encode readable labels like “Education” or “Python”).

## What Changes

- A **server-side pipeline** that reads each uploaded PDF from disk (same files as ingestion), extracts **plain text** with the existing PDF stack (e.g. `PyPDFLoader` / pypdf), and derives:
  - **Category distribution** for a pie chart: counts (and optionally per-file breakdown) for a fixed set of **resume section categories** detected via heading/keyword heuristics on the raw text (e.g. Experience, Education, Skills, Summary, Projects, Other).
  - **Skill frequency** for a bar (or horizontal bar) chart: match normalized substrings against a **maintained skills lexicon** (and/or regex patterns for common tech tokens), aggregated across all uploaded PDFs, with configurable top-N.
- A **JSON API** that returns these aggregates so the UI does not need to parse PDFs in the browser.
- A **static analytics page** (or an extension of an existing page) that renders a **Plotly pie chart** and **Plotly bar chart** from that API, with empty-state handling when no PDFs are present.

Explicit **non-use** for this feature: Chroma embeddings, UMAP coordinates, cluster labels from the vector pipeline, or any chart series derived from embedding dimensions.

## Capabilities

### New Capabilities

- `resume-text-analytics`: Extract text from PDFs on disk, classify detected sections into resume categories, and expose aggregate counts for visualization.
- `resume-skills-frequency`: Match extracted text against a skills lexicon and expose ranked skill frequencies across the corpus.
- `resume-analytics-ui`: Plotly pie + bar charts driven only by analytics API payloads (text-derived statistics).

### Modified Capabilities

## Impact

- **New modules** (suggested): e.g. `app/services/resume_analytics.py` (text extraction, categorization, skill matching), optional `app/data/skills_lexicon.txt` or inline list in code for the course scope.
- **New router** (suggested): e.g. `GET /api/resumes/analytics` returning category counts + top skills (exact schema in design).
- **New static page** (suggested): e.g. `app/static/analytics.html` and `GET /analytics` in `app/main.py`, mirroring `/visualize`.
- **Dependencies**: Prefer **no** new heavy ML deps if heuristics + lexicon suffice; optional small additions only if justified in design.
- **Performance**: Re-scanning all PDFs on each request is acceptable for a small course corpus; optional simple in-process cache keyed by file mtime if needed.
