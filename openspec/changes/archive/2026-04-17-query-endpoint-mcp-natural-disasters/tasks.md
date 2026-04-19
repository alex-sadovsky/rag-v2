## 1. Wire `mcp_csv_server` into the FastAPI app

- [x] 1.1 Add **`mcp_csv_server`** as a **path dependency** (or workspace equivalent) in the **root** `pyproject.toml` so `from mcp_csv_server.disasters import run_query_from_loaded` works in `app/`.
- [x] 1.2 Install / lock dependencies and confirm **`pandas`** resolves; run a quick import smoke test.

## 2. Intent routing for `POST /query`

- [x] 2.1 Implement **`is_natural_disaster_query(question: str) -> bool`** (or similar) in a small module under `app/services/` using the **keyword / heuristic** rules from design (tunable list of terms).
- [x] 2.2 (Optional) Add settings in `app/config.py` for toggles or extra keywords if needed.

## 3. Natural language → tool arguments

- [x] 3.1 Implement **`question_to_disaster_arguments(question: str) -> dict[str, Any]`** — start with **rules/regex** for years, ISO, country, and disaster-type hints; default sensible **`limit`** (e.g. 50) and **`datasets`: `"both"`**.
- [x] 3.2 Pipe the dict through existing **`params_from_arguments`** / reuse **`run_query_from_loaded`** so validation matches the MCP tool exactly.
- [x] 3.3 (Optional follow-up) Add an LLM-based extractor with strict JSON schema; guard with settings.

## 4. Integrate into the query endpoint

- [x] 4.1 In `app/routers/query.py` (or delegated service), **if** disaster intent: call **`run_query_from_loaded(arguments)`**, build **`QueryResponse`** with **`answer`** = tool text and **`sources`** per design (empty or synthetic provenance chunk).
- [x] 4.2 Adjust **503** behavior: allow disaster responses when Anthropic is only needed for RAG (see design); document in endpoint docstring / OpenAPI.
- [x] 4.3 Map **`FileNotFoundError`** / **`ValueError`** from the disaster path to appropriate **HTTP errors** or structured error bodies consistent with the app.

## 5. Tests

- [x] 5.1 Unit tests: **`is_natural_disaster_query`** true/false cases (including at least one “should stay RAG” case).
- [x] 5.2 Unit or integration tests: **`question_to_disaster_arguments`** produces arguments accepted by **`params_from_arguments`** (use **`MCP_DISASTER_CSV_DIR`** with tiny fixture CSVs if full EMDAT files are not in CI).
- [x] 5.3 Optional: **`httpx`** test that **`POST /query`** returns disaster-formatted **`answer`** when the body clearly requests disaster data (skip if environment lacks data files).

## 6. Documentation

- [x] 6.1 Short note in **`README.md`** or existing API docs: **`/query`** may answer from **EM-DAT CSVs** when the question targets natural-disaster data, aligned with MCP **`query_natural_disasters`**.
