## 1. Dependencies and data paths

- [x] 1.1 Add **`pandas`** to `mcp_csv_server/pyproject.toml` `dependencies` with a sensible lower bound (e.g. `pandas>=2.0`).
- [x] 1.2 Introduce a small **path helper** that resolves `dataset/csv/` relative to the **repository root** (walk parents for a marker such as `pyproject.toml` **or** `dataset/csv` directory) and allows override via **`MCP_DISASTER_CSV_DIR`** (or similarly named) for tests.

## 2. Pandas loading and unified schema

- [x] 2.1 Implement a module (e.g. `mcp_csv_server/disasters.py`) that loads **both** files:
  - `dataset/csv/1900_2021_DISASTERS.xlsx - emdat data.csv`
  - `dataset/csv/1970-2021_DISASTERS.xlsx - emdat data.csv`
- [x] 2.2 **Union** columns, **`concat`** vertically, add a **`dataset`** (or `source_file`) column; handle the extra `Dis No` / `Reconstruction Costs` columns without dropping data.
- [x] 2.3 Cache the combined **`DataFrame`** after first successful load; surface clear errors if files are missing.

## 3. Query API (Pandas-only)

- [x] 3.1 Implement filtering/sorting per `design.md`: **`Year`** (or documented alternative), optional **`ISO`** / **`Country`**, optional **`Disaster Type`** / **`Disaster Subgroup`**, `limit`, optional `columns`, optional `sort_by`.
- [x] 3.2 Enforce **hard caps** on `limit` and on total serialized text length; truncate with an explicit message when needed.
- [x] 3.3 Format results as human-readable **text** (and optional compact **table** for small row counts).

## 4. MCP tool registration

- [x] 4.1 Define the tool in MCP (`list_tools`) with a JSON **input schema** matching the parameters (use SDK-supported schema fields).
- [x] 4.2 Implement **`call_tool`** dispatch for the new tool name, mapping arguments to the query function; return `isError=True` with a clear message on validation failures.
- [x] 4.3 Update server **`instructions`** string to describe the disaster query capability (replace “no tools” placeholder text).

## 5. Documentation and tests

- [x] 5.1 Update `mcp_csv_server/README.md`: dependency install, **`python -m mcp_csv_server`**, Cursor MCP JSON snippet, env var for CSV dir, tool parameter summary.
- [x] 5.2 Update `mcp_csv_server/tests/`: remove or adjust **“zero tools”** assertions; add tests for **tool listing**, **argument validation**, and **query logic** (prefer synthetic DataFrames for speed).
- [x] 5.3 Optional manual smoke: run server, confirm client sees the tool and a sample query returns rows when CSVs are present.
