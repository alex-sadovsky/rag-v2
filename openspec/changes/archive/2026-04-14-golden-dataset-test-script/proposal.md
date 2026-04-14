## Why

The repository already ships a structured **golden dataset** in `golden_dataset.txt` (JSON: cases with `question`, `k`, `must_contain` / `must_not_contain`, optional `reference_answer` and `judge_criteria`). Today there is no repeatable way to run those cases against the live RAG stack and get a clear pass/fail signal. A small **evaluation script** closes that gap: developers can regression-test retrieval + generation after ingestion or config changes without hand-curling each question.

## What Changes

- Add a **Python CLI script** (e.g. under `scripts/` or project root) that:
  - Loads `golden_dataset.txt` as JSON (same schema as today: `schema_version`, `defaults`, `cases[]`).
  - For each case, issues `POST /query` with `question` and per-case or default `k`.
  - Evaluates answers using the **cheap guards** defined in the dataset: **case-insensitive** substring checks for `must_contain` and `must_not_contain`.
  - Prints a concise per-case report (id, PASS/FAIL, optional snippet of failure reason) and exits with **non-zero** if any case fails (suitable for CI or local gates).
- Document prerequisites in script help or README: **running API** with indexed PDFs and **`ANTHROPIC_API_KEY`** configured (same as normal `/query` usage).

**Out of scope for this change (optional follow-ups):** LLM-as-judge using `judge_criteria`, embedding similarity to `reference_answer`, or automated retrieval-only checks using `retrieval.hint_keywords`. The dataset fields remain available for future extensions.

## Capabilities

### New Capabilities

- None (tooling only; no new REST surface).

### Modified Capabilities

- None required. Optional note in `rag-query`-related docs that golden evaluation exists.

## Impact

- New script file(s) and possibly `pyproject.toml` script entry or documented `python -m ...` invocation.
- No changes to `app/` required unless we choose an in-process mode that imports `run_rag_query` (design may prefer HTTP-only to match deployment).
