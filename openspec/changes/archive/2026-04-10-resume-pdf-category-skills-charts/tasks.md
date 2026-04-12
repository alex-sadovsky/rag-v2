## 1. Analytics service (PDF text only)

- [x] 1.1 Add `app/services/resume_analytics.py` with a function to list `*.pdf` paths under `settings.uploads_dir` and return empty analytics when none exist.
- [x] 1.2 For each PDF, load text via `PyPDFLoader` (same as `ingest_pdf`), producing one full-text string per file.
- [x] 1.3 Implement section heading detection and a line-scanning state machine that assigns text spans to category buckets (`experience`, `education`, `skills`, `summary`, `projects`, `certifications`, `other`); aggregate **character counts** (or another documented unit) per category across all files.
- [x] 1.4 Add a skills lexicon (e.g. `app/data/skills_lexicon.txt` or a module-level tuple) with longer multi-word skills listed before shorter ones to reduce greedy matching issues.
- [x] 1.5 Implement skill matching with **per-file deduplication** per skill, then sum counts across files for top-N skills; accept `top_skills` parameter (default 15).

## 2. API

- [x] 2.1 Define Pydantic response models for `GET /api/resumes/analytics` (categories + skills + `files_scanned` + optional warnings).
- [x] 2.2 Create `app/routers/resume_analytics.py` (or extend an existing router if preferred) implementing `GET /api/resumes/analytics` with query params as per design (`top_skills`, etc.).
- [x] 2.3 Register the new router in `app/routers/__init__.py`. Ensure **no** dependency on `vectors` or Chroma for this endpoint.

## 3. Frontend

- [x] 3.1 Add `app/static/analytics.html` using Plotly from CDN: pie chart for categories, horizontal bar chart for skills.
- [x] 3.2 On load, `fetch('/api/resumes/analytics')`, handle errors and **empty state** (`files_scanned === 0` or no categories/skills).
- [x] 3.3 Add `GET /analytics` in `app/main.py` returning `FileResponse` for `analytics.html`, parallel to `/visualize`.

## 4. Documentation

- [x] 4.1 Update `README.md` with the new resume analytics surface: document `GET /api/resumes/analytics` (purpose, query parameters such as `top_skills`, example JSON response shape), how to call it (e.g. browser, `curl`, or fetch from the app origin), and the `/analytics` page for the pie and skills charts. Note that analytics are derived from **PDF text on disk**, not from embeddings or vector coordinates.

## 5. Verification

- [x] 5.1 Upload one or more sample resume PDFs; call `GET /api/resumes/analytics` and confirm JSON fields are populated from **text extraction**, not from vector endpoints.
- [x] 5.2 Open `/analytics` in a browser: pie and bar charts render; empty uploads folder shows a clear message.
- [x] 5.3 Confirm `/visualize` still works and analytics charts do **not** change when only re-running queries/embeddings without changing PDF files (optional sanity check).
