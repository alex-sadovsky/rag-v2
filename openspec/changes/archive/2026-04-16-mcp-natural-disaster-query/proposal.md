## Why

The repo already ships a **stdio MCP server** (`mcp_csv_server/`) with **no tools**, intended as a hook for CSV-backed assistants. Operators need a **single MCP tool** that answers questions about **natural disasters** using the **EM-DAT–style** exports checked into `dataset/csv/`, without hand-editing CSVs or leaving the chat workflow.

**Pandas** is the right fit for filtering, sorting, and light aggregation on tabular disaster records at this scale.

## What Changes

- Add **`pandas`** (and any minimal typing/helpers) to the **`mcp-csv-server`** package dependencies.
- Load **both** CSV assets under `dataset/csv/`:
  - `1900_2021_DISASTERS.xlsx - emdat data.csv` — long historical series (columns omit `Dis No` and use a slightly different damage column set than the newer extract).
  - `1970-2021_DISASTERS.xlsx - emdat data.csv` — includes `Dis No` and `Reconstruction Costs ('000 US$)`.
- Implement **one MCP tool** (name TBD in implementation; e.g. `query_natural_disasters`) that:
  - Accepts structured parameters (e.g. year range, country / ISO, disaster type or subgroup, row limit) rather than raw SQL from the model, to keep behavior safe and predictable.
  - Returns **text** (and optionally **small** tabular excerpts) suitable for the host — with a **row cap** to avoid huge payloads.
- **Normalize** the two frames where schemas differ (align columns, add a `source_file` or `dataset` column so results are traceable).
- Update **`mcp_csv_server` README** with Cursor MCP config and tool description; extend **tests** beyond “zero tools” (smoke + handler behavior).

## Capabilities

### New Capabilities

- **`mcp-csv-pandas` / disaster query**: MCP tool(s) backed by Pandas over the two checked-in disaster CSVs under `dataset/csv/`.

### Modified Capabilities

- **`mcp-csv-pandas`**: Server **no longer** exposes an empty tool list — at least one tool is registered for disaster queries.

## Impact

- **`mcp_csv_server/pyproject.toml`** — add `pandas`; version pin consistent with Python ≥3.11.
- **`mcp_csv_server/mcp_csv_server/`** — new module(s) for data load + query logic; **`server.py`** — register tool + `call_tool` dispatch.
- **`mcp_csv_server/README.md`** — document the tool and paths to CSVs (repo-relative).
- **`mcp_csv_server/tests/`** — update tests for non-empty tools and query smoke (optional: monkeypatch paths for small fixtures if needed).
