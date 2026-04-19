# mcp-csv-server

Stdio [Model Context Protocol](https://modelcontextprotocol.io/) server for this repository. It exposes **`query_natural_disasters`**, which uses **Pandas** to filter EM-DAT-style disaster CSVs under `dataset/csv/`.

## Data files

By default the server loads (from the **repository root**):

- `dataset/csv/1900_2021_DISASTERS.xlsx - emdat data.csv`
- `dataset/csv/1970-2021_DISASTERS.xlsx - emdat data.csv`

Paths are resolved by walking parents of the installed package until a `dataset/csv` directory is found. Override the directory with:

| Variable | Purpose |
|----------|---------|
| `MCP_DISASTER_CSV_DIR` | Absolute path to the folder **containing** the two CSV files (for tests or non-standard layouts). |

## Tool: `query_natural_disasters`

Structured parameters (JSON):

| Parameter | Description |
|-----------|-------------|
| `datasets` | `"1900"`, `"1970"`, or `"both"` (default). Selects the 1900–2021 file, the 1970–2021 file, or both (union). |
| `year_min` / `year_max` | Inclusive filter on **`Year`**. |
| `country` | Case-insensitive **substring** on `Country`. |
| `iso` | Exact **ISO** code (case-insensitive). Prefer this when known. |
| `disaster_type` | Case-insensitive substring on `Disaster Type`. |
| `disaster_subgroup` | Case-insensitive substring on `Disaster Subgroup`. |
| `limit` | Max rows returned (default **50**, hard cap **500**). |
| `columns` | Optional list of column names to include. |
| `sort_by` / `ascending` | Optional sort before applying `limit`. |
| `max_chars` | Max total characters in the text response (default **100000**). |

Responses are plain text with a short summary; for smaller result sets, a compact **markdown table** may be used.

## Install

From the repository root (or this directory):

```bash
pip install -e "./mcp_csv_server_pkg[dev]"
```

Requires **Python ≥3.11**, **`mcp`**, and **`pandas`**.

## Run (manual smoke)

```bash
python -m mcp_csv_server
```

The process waits on stdio for an MCP host (e.g. Cursor). Running it alone in a terminal will appear idle until a client connects.

## Cursor MCP configuration

Add a server entry (user `mcp.json` or project `.cursor/mcp.json`) similar to:

```json
{
  "mcpServers": {
    "mcp-csv-pandas": {
      "command": "python",
      "args": ["-m", "mcp_csv_server"],
      "cwd": "Y:/home/alex/develop/ai/architect-course/rag-v2"
    }
  }
}
```

Use the same Python interpreter where `mcp_csv_server` is installed. Set **`cwd`** to the **repository root** so discovery of `dataset/csv` via package location stays consistent, or set **`MCP_DISASTER_CSV_DIR`** to the folder that contains the CSV files.

## Tests

```bash
python -m pytest mcp_csv_server_pkg/tests -q
```
