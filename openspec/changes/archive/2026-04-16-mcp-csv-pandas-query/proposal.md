## Why

Cursor and other MCP hosts integrate with **stdio MCP servers**. This repo will eventually add a server that uses **Pandas** to query CSV data from chat, but **tool definitions and handlers are deferred**: the first step is a **running MCP process** that connects cleanly and exposes **no tools**, so follow-up work can add CSV/Pandas tools without reshaping the server skeleton.

## What Changes

- New **Python MCP server** package (stdio transport) that:
  - Starts and completes the MCP handshake with the host
  - Registers **zero** tools — the server does **not** list or return any tools to the client
- Dependencies for **this** change: official MCP Python SDK (or equivalent) only; **no** `pandas` and **no** CSV loading until a later change
- Documentation for **Cursor MCP config** (how to register the server) and a minimal smoke check that the process stays up

## Capabilities

### New Capabilities

- `mcp-csv-pandas`: Placeholder namespace — **empty-tool** MCP server process only in this change; CSV/Pandas behavior comes later

### Modified Capabilities

- None (additive; does not change existing FastAPI routes or RAG behavior)

## Impact

- New directory (e.g. `mcp_csv_server/` or `servers/mcp-csv-pandas/`) with `pyproject.toml`
- Short README section or `mcp_csv_server/README.md` — run instructions and explicit note that **tools are not implemented yet**
