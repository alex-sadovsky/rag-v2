## 1. Dataset loading and CLI

- [x] 1.1 Add the evaluation script module (recommended: `scripts/run_golden_dataset.py` or equivalent) with argument parsing: `--base-url` (default `http://127.0.0.1:8000`), `--dataset` (default path to repo `golden_dataset.txt`), optional `--case` to filter by `id`, optional timeout for HTTP calls.
- [x] 1.2 Parse `golden_dataset.txt` as UTF-8 JSON; validate presence of `cases` list; apply `defaults.k` when a case has no `k`.

## 2. HTTP evaluation loop

- [x] 2.1 For each selected case, `POST {base_url}/query` with `Content-Type: application/json` and body `{"question": <case.question>, "k": <resolved k>}`.
- [x] 2.2 Read JSON response; extract `answer` string; on HTTP or JSON errors, print diagnostic and exit non-zero.

## 3. Assertions and reporting

- [x] 3.1 Implement case-insensitive `must_contain` and `must_not_contain` checks on `answer`.
- [x] 3.2 Print per-case PASS/FAIL with `id`; on FAIL, indicate missing required substring or forbidden substring found.
- [x] 3.3 Exit `0` if all cases pass, `1` otherwise.

## 4. Dependencies and documentation

- [x] 4.1 Use `httpx` or stdlib HTTP per `pyproject.toml` — avoid adding dependencies if stdlib suffices.
- [x] 4.2 Add a short usage blurb: prerequisites (server running, PDFs ingested, `ANTHROPIC_API_KEY` set), example command from repo root.

## 5. Verification

- [ ] 5.1 Manually run the script against a local server with the course resume PDFs indexed; confirm cases behave as expected.
- [x] 5.2 Optionally add a **unit test** that feeds a tiny inline JSON fixture to the pure check functions (no network) if those functions are factored out for testability.
