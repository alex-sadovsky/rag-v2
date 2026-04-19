## Context

The repo is a **FastAPI** RAG demo (`app/`, `pyproject.toml`, Python **≥3.11**). This change adds a **standalone** MCP process for **Cursor** (or similar) over **stdio**. Future work will add **Pandas**-backed tools for CSV Q&A; **this** change intentionally ships **no tools** so the host sees an **empty tool list**.

## Goals / Non-Goals

**Goals:**

- Implement an MCP server using the **official MCP Python SDK** (stdio transport)
- Register **no** `@tool` / `list_tools` entries — **zero tools** exposed to the client
- Clean entrypoint (e.g. `python -m …`) and documented Cursor MCP configuration
- Keep dependencies minimal: **MCP SDK only** for this change

**Non-Goals (explicitly out of scope for this change):**

- Any MCP **tools** (including CSV load, schema, filter, aggregate, or formatting helpers)
- **`pandas`**, CSV paths, caching, or env vars such as `MCP_CSV_PATH` — reserved for a follow-up change
- Embedding the MCP into the FastAPI process or HTTP fronting
- Prompts, resources, or sampling behavior beyond what the empty server requires to run

## Decisions

### Transport and entrypoint

**stdio MCP** — `command` + `args` in the host config; single process, no network listener.

### Empty tool surface

The server **must not** advertise tools: `list_tools` resolves to an **empty** list (or equivalent SDK pattern so the client receives **no** tools). No stub tools “for later”; additions happen in a separate change.

### Dependencies

- **This change:** MCP Python package only.
- **Later change:** add `pandas`, CSV configuration, and actual tools.

### Package layout

New top-level package directory containing:

- `server.py` (or equivalent) — create MCP server, **no** tool registration
- `__main__.py` — stdio entrypoint
- `pyproject.toml` — Python 3.11+, MCP dependency

### Testing

- **Smoke:** subprocess or manual run — process starts and accepts stdio without crashing
- **Optional:** if the SDK allows, assert `list_tools` is empty in a unit test

## Risks / Trade-offs

- **Host UX:** Until tools land, the server adds no chat-side capability; that is intentional.
- **Follow-up coordination:** The next change should add `pandas`, env config, and tools in one coherent pass to avoid orphan dependencies.
