## Why

The FastAPI **`POST /query`** endpoint today always runs **RAG** over indexed PDF chunks (`run_rag_query`). Questions about **natural disasters** backed by the repo’s **EM-DAT–style CSVs** are a poor fit for vector search: users need **tabular, filterable facts** (year, country, disaster type) that already exist in `dataset/csv/` and are exposed to Cursor via the **`query_natural_disasters`** MCP tool.

Routing those questions to the **same query logic** as that tool keeps answers **consistent** with MCP-assisted chat and avoids irrelevant PDF retrieval.

## What Changes

- **Detect** when a `/query` request is asking about **natural disasters / EM-DAT-style data** (vs. general document Q&A).
- For those requests, **run the natural-disaster query path** that matches the MCP tool **`query_natural_disasters`**: structured filters over the bundled CSVs (Pandas), **not** Chroma retrieval.
- Map the user’s **natural-language question** into **tool arguments** (year range, country / ISO, disaster type/subgroup, limit, etc.) using a defined strategy (see design).
- Return a **`QueryResponse`** whose **`answer`** contains the tool’s text output (markdown table or plain text); **`sources`** may be empty or carry a **synthetic** citation to the dataset (implementation detail in design).

For all **other** questions, behavior stays **unchanged** (existing RAG pipeline).

## Capabilities

### New Capabilities

- **`rag-query` / disaster branch**: Optional path on `POST /query` for natural-disaster questions using **`mcp_csv_server`** disaster query implementation (aligned with MCP tool **`query_natural_disasters`**).

### Modified Capabilities

- **`rag-query`**: Same endpoint and response model; internal routing adds a **disaster** branch before vector retrieval when intent matches.

## Impact

- **`app/`** — router and/or service layer: intent detection + call into disaster query; possibly new settings for routing/tuning.
- **`pyproject.toml` (root)** — declare dependency on the local **`mcp_csv_server`** package (or extract shared query code; see design).
- **Tests** — unit tests for routing and for argument mapping / integration with `run_query_from_loaded` (may use `MCP_DISASTER_CSV_DIR` or small fixtures).
