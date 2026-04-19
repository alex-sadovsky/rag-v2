## Context

- **FastAPI RAG app** lives under `app/`; **MCP** is a **separate** package `mcp_csv_server/` (stdio), already wired with the official **MCP Python SDK** and **empty** `list_tools`.
- Disaster data is **versioned in-repo** as two CSV files in `dataset/csv/`:
  - **`1900_2021_DISASTERS.xlsx - emdat data.csv`** — wide year range; first column is `Year` (no `Dis No`).
  - **`1970-2021_DISASTERS.xlsx - emdat data.csv`** — includes `Dis No` as first column and an extra `Reconstruction Costs ('000 US$)` column not present in the 1900 extract.
- Schemas are **mostly** aligned on shared EM-DAT-style headers but are **not identical**; Pandas loads must **union** columns (missing values as `NaN`) and tag rows with **`dataset`** or **`source_file`** for transparency.

## Goals / Non-Goals

**Goals:**

- Register **exactly one** primary tool for **natural disaster** lookups (filter + sort + optional aggregates such as `count` / `sum` on numeric columns where safe).
- Use **Pandas** for all tabular operations (no SQL engine requirement).
- Resolve CSV paths relative to the **repository root** (e.g. `dataset/csv/...`) with a clear override via **environment variable** (e.g. `MCP_DISASTER_CSV_DIR`) for tests or relocated checkouts.
- Enforce **output limits** (max rows returned, max string length) so MCP responses stay within host limits.
- Keep the MCP process **single-purpose**: still **no** FastAPI coupling.

**Non-Goals:**

- Ingesting these CSVs into Chroma or the RAG pipeline.
- Arbitrary **user-supplied Python** or **raw pandas eval** from the model (unsafe); parameters should be **explicit fields** on the tool.
- Perfect EM-DAT domain modeling (ontology, geocoding); treat rows as **flat tables**.

## Decisions

### 1. Tool contract (structured parameters)

Expose one tool, e.g. **`query_natural_disasters`**, with JSON parameters such as:

| Parameter | Purpose |
|-----------|---------|
| `datasets` | Which file(s) to query: `1900`, `1970`, or `both` (default `both`). |
| `year_min` / `year_max` | Filter on `Year` or `Start Year` (document which; prefer **`Year`** for consistency). |
| `country` | Optional substring match on `Country` (case-insensitive) **or** optional `iso` for exact `ISO` code. |
| `disaster_type` / `disaster_subgroup` | Optional substring or exact match on the respective columns (pick one strategy and document). |
| `limit` | Max rows (default small, e.g. 50; hard cap e.g. 500). |
| `columns` | Optional allowlist of column names to reduce payload. |
| `sort_by` / `ascending` | Optional ordering before `limit`. |

Return `CallToolResult` with **`text/plain`** summary plus optional **markdown table** for small previews.

**Rationale:** Structured args avoid code injection and make testing deterministic.

### 2. Schema alignment

- Read both CSVs with `pandas.read_csv` (let Pandas infer; set `low_memory=False` if needed for mixed types).
- Build a **unified column list** = union of both header sets; **`concat`** with `sort=False` so missing columns appear as `NaN`.
- Add **`dataset`** ∈ `{ "1900-2021", "1970-2021" }` (or file basename) on each row.

### 3. Caching

- **Lazy load** on first tool call (module-level or server singleton) to avoid slow startup; optional simple **mtime** check if files can change during dev.

### 4. Dependencies

- Add **`pandas`** to `mcp_csv_server/pyproject.toml` dependencies.

### 5. Testing

- Unit tests for filter logic using **tiny** inline DataFrames or temp CSVs (do not require full EMDAT files in CI if too heavy — prefer synthetic frames that mirror column names).
- Integration smoke: tool is **listed** and **callable** with parameters that return a non-error result when pointed at real CSVs in dev.

## Risks / Trade-offs

- **Schema drift** between the two files may grow if datasets are replaced; union-column approach absorbs extra columns but callers must tolerate new fields.
- **Large files** (~16k + ~14k rows) are fine in memory for local MCP but **must** respect `limit` to keep responses small.
- **Substring** matching on `Country` can false-positive; document and prefer **`iso`** when the user knows it.
