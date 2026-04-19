## 1. Scaffold MCP package (no tools)

- [x] 1.1 Add a new directory for the MCP server (e.g. `mcp_csv_server/`) with its own `pyproject.toml` listing only the official MCP Python package (and `pytest` under dev deps). **Do not** add `pandas` in this change.
- [x] 1.2 Implement stdio MCP server startup using the SDK’s supported pattern so the process speaks MCP to the host.
- [x] 1.3 Ensure **no tools** are registered — `list_tools` must yield an **empty** list (or SDK equivalent). Do **not** add placeholder or stub tools.

## 2. Entrypoint and docs

- [x] 2.1 Add a runnable entrypoint (e.g. `python -m mcp_csv_server` via `__main__.py`).
- [x] 2.2 Document Cursor MCP configuration (`command`, `args`) and state clearly that **tools are not implemented** and will come in a later change.

## 3. Verification

- [x] 3.1 Smoke-check: server starts and stays compatible with stdio MCP (manual or light automated check).
- [x] 3.2 Optional: unit test that the registered tool count is **zero** if the SDK exposes a stable way to assert it.
