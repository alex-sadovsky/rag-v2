## Context

- `golden_dataset.txt` is JSON (not `.json` extension) with `cases[]`. Each case includes `id`, `question`, optional `k`, `must_contain`, `must_not_contain`, plus human-oriented `reference_answer` / `judge_criteria` / `retrieval` metadata for richer evaluation later.
- Production RAG answers come from `POST /query` (`app/routers/query.py`) → `run_rag_query` (`app/services/query.py`), which uses conditional hybrid retrieval and Claude Haiku with a grounding system prompt.
- The vector store is **in-memory**; evaluators must run queries in the **same process lifetime** as ingestion, or accept that a separate long-running server already has the right PDFs loaded.

## Goals / Non-Goals

**Goals:**

- **Single source of truth** — read cases only from `golden_dataset.txt` (path configurable via CLI flag, defaulting to the file at repo root next to `README.md`).
- **Deterministic cheap checks** — implement `must_contain` / `must_not_contain` as **case-insensitive** substring tests on the returned `answer` string (per dataset description).
- **HTTP client to `/query`** — use `httpx` or stdlib `urllib` to POST JSON `{"question": "...", "k": N}` to a configurable base URL (default `http://127.0.0.1:8000`). This keeps the script aligned with real deployment and avoids importing app internals.
- **Usable defaults** — merge `defaults.k` from the file when a case omits `k`; respect per-case `k` when present.
- **Operator-friendly output** — one line per case with id and status; on failure, show which substring rule broke; exit code `0` all pass, `1` any failure (and non-zero on HTTP/JSON errors as appropriate).

**Non-Goals:**

- Calling Anthropic twice per case for LLM judging.
- Starting the FastAPI server or uploading PDFs (document only).
- Storing results to files unless trivial (optional `--json-out` can be a stretch goal; keep MVP stdout-only).

## Decisions

### 1. Transport: HTTP only

**Choice:** Script is a thin HTTP client.

**Rationale:** Matches TLS/auth-less local usage; works against `main.py` or uvicorn; no need to wire `Settings` or mock vectorstores in the script.

**Alternative:** Import `run_rag_query` in-process — faster for developers but duplicates environment setup and does not catch router-layer issues.

### 2. Path to dataset

**Choice:** CLI flag `--dataset` with default resolving to `golden_dataset.txt` relative to the **current working directory** or, preferably, **script location / repo root** (document one clear rule: e.g. resolve from `Path(__file__).resolve().parents[1] / "golden_dataset.txt"` if the script lives in `scripts/`).

### 3. Validation rules

- For each string in `must_contain`: `s.lower() in answer.lower()`.
- For each string in `must_not_contain`: `s.lower() not in answer.lower()`.
- Empty lists: no constraints from that side.

### 4. Error handling

- If `POST /query` returns **503**, print a clear message (missing `ANTHROPIC_API_KEY`).
- If connection refused, suggest starting the server and ingesting PDFs.
- Parse JSON response; require `answer` key.

### 5. Dependencies

- Prefer **`httpx`** if already in `pyproject.toml`; otherwise **`urllib.request`** to avoid new deps — check project before implementation.

## Risks / Trade-offs

- **Flaky LLM outputs** — substring guards may occasionally fail on rephrasing; `must_*` in the dataset should be chosen as stable anchors (project already does this for several cases).
- **Indexed content** — failures may reflect missing uploads rather than code bugs; document the workflow (upload resume PDFs, then run script).

## Open Points

- Whether to add optional `--case <id>` to run a subset (recommended in tasks). -- DO NOT ADD
- Exact script path (`scripts/run_golden_dataset.py` vs `eval_golden.py` at repo root) — pick one consistent with existing repo layout (`scripts/` may need to be created). -- Use `scripts/run_golden_dataset.py`
