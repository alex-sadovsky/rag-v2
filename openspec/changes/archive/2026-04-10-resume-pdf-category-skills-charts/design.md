## Context

The FastAPI app already ingests PDFs with `PyPDFLoader`, splits text for Chroma, and exposes vector visualization that uses **embeddings and UMAP**. This change adds **readability-focused analytics**: charts that summarize **what the PDFs say**, by scanning **full document text** from files under the configured uploads directory (`settings.uploads_dir`). No chart in this feature may use vector coordinates, embedding components, or Chroma similarity scores as its data source.

## Goals / Non-Goals

**Goals:**

- **Pie chart**: Show the distribution of **resume section categories** across the corpus (or per document, if we later extend — v1 can be global counts only).
- **Bar chart**: Show the **most common skills** (top N) by frequency across all PDFs.
- **Single source of truth**: Statistics computed in Python from **extracted PDF text** on disk.
- **REST JSON API** consumed by a small Plotly static page (CDN), consistent with `/visualize`.
- **Clear empty state** when `uploads/` has no PDFs or text extraction yields nothing useful.

**Non-Goals:**

- Using embeddings, Chroma, or UMAP to produce these two charts.
- Perfect NLP (no requirement for spaCy/transformers unless explicitly added later).
- OCR for scanned PDFs (text-based PDFs only; document limitation).
- Persistent analytics database (recompute from files each time, unless a cache is added as an optimization).

## Decisions

### 1. Text extraction path

**Decision**: Re-read each `*.pdf` under `uploads_dir` using the same loader as ingestion (`PyPDFLoader`) and concatenate page text (or join with newlines) into one string per file.

**Rationale**: Aligns with existing dependencies and behavior; avoids a second storage format.

**Alternatives**: pdfplumber — better layout for some PDFs but adds dependency; defer unless extraction quality is insufficient in testing.

### 2. What “resume categories” means

**Decision**: A **fixed enum** of high-level section buckets, assigned by **heuristic line/block classification**:

- Scan lines (split on newlines); treat a line as a **heading** if it matches a case-insensitive keyword list (e.g. “experience”, “work history”, “education”, “skills”, “summary”, “objective”, “projects”, “certifications”).
- Map each heading to one of: `experience`, `education`, `skills`, `summary`, `projects`, `certifications`, `other`.
- Count **characters or line counts** attributed to each section until the next heading (simple finite-state parser over the full text).

**Rationale**: Deterministic, testable, no ML. Produces a meaningful pie chart for typical resume layouts.

**Risk**: Messy PDFs may land mostly in `other`. Mitigation: document limitation; optional future LLM pass is out of scope.

### 3. Skill extraction

**Decision**: **Lexicon-based** matching: a sorted list of skill strings (longer phrases first). For each resume’s full text (lower-cased), find non-overlapping matches and count **one hit per skill per file** (dedupe per document) or **raw occurrence counts** — **Decision**: **per-file dedupe** for frequency across corpus (avoids one resume repeating “Python” 50 times from a project list dominating the chart). State this clearly in API docs.

**Rationale**: Predictable for coursework; easy to extend the lexicon.

**Alternatives**: Full regex for `\b[A-Z][a-z]+\b` — too noisy; rejected for v1.

### 4. API shape

**Decision**: One endpoint, e.g. `GET /api/resumes/analytics`, returning JSON:

```json
{
  "files_scanned": 3,
  "categories": [
    { "id": "experience", "label": "Experience", "count": 1200 },
    { "id": "education", "label": "Education", "count": 400 }
  ],
  "skills": [
    { "skill": "Python", "count": 3 },
    { "skill": "SQL", "count": 2 }
  ]
}
```

- `categories[].count`: use **content units** consistently (e.g. character count per section body) so the pie represents “how much text falls under each section type,” not file counts.

Optional query params: `top_skills` (default 15), `include_other` for pie.

### 5. UI placement

**Decision**: New static page `app/static/analytics.html`, served at `GET /analytics` via `FileResponse`, same pattern as `/visualize`.

Charts: Plotly pie (`categories`), Plotly horizontal bar (`skills`). Fetch `/api/resumes/analytics` on load; show spinner then render or empty message.

### 6. Explicit separation from vector visualization

**Decision**: No import from `app/services/vectors.py` in the analytics service. Analytics router only uses uploads path + new analytics service. Document in code comment at router level to prevent accidental coupling.

## Risks / Trade-offs

- **Heuristic categories** can misclassify unusual resumes → pie chart is indicative, not ground truth.
- **Lexicon coverage** limits skill chart → start with a sensible default list (languages, cloud, DB, common tools) in-repo.
- **Full rescans** on each request may lag with many large PDFs → optional mtime cache in a follow-up.

## Migration Plan

1. Add `resume_analytics` service: extract text, parse sections, aggregate categories, match skills.
2. Add `GET /api/resumes/analytics` router; register router.
3. Add `analytics.html` + `/analytics` route.
4. Manual test: upload sample PDFs, open `/analytics`, confirm charts change when lexicon or files change (not when re-embedding).
