## Context

- **`POST /query`** is implemented in `app/routers/query.py` and delegates to `app.services.query.run_rag_query` (Chroma + Claude).
- The repo already ships **`mcp_csv_server`**, which registers MCP tool **`query_natural_disasters`** and implements it via `mcp_csv_server.disasters.run_query_from_loaded` (same structured parameters as `server.py`’s `inputSchema`).
- Disaster CSVs live under **`dataset/csv/`** (override **`MCP_DISASTER_CSV_DIR`** for tests or alternate checkouts).

## Goals / Non-Goals

**Goals:**

- When the user’s **question targets natural-disaster / EM-DAT tabular data**, answer using **`run_query_from_loaded`** (or an equally thin wrapper), so results match the **`query_natural_disasters`** MCP tool.
- Keep **one HTTP API** (`POST /query`); no new public route required unless product asks for it later.
- Translate **natural language → tool arguments** safely (structured fields only; no arbitrary code execution).

**Non-Goals:**

- Spawning a **stdio MCP subprocess** from FastAPI on every request (heavy, brittle). The **authoritative behavior** is the shared Python implementation already used by the MCP server.
- Ingesting disaster CSVs into Chroma for this change.
- Perfect NLU; start with a **practical** router + parameter extraction approach (below).

## Decisions

### 1. “Use MCP” in practice

**Decision:** The API **imports and calls** `run_query_from_loaded` from **`mcp_csv_server.disasters`** (after adding **`mcp_csv_server`** as a dependency of the FastAPI app). That function **is** the **`query_natural_disasters`** tool body.

**Rationale:** Same inputs/outputs as the MCP tool without MCP transport overhead. Document this in code comments so “MCP tool” and “API path” stay aligned.

**Alternative (not default):** A long-lived MCP client over stdio — only if a future requirement mandates protocol-level isolation.

### 2. Dependency wiring

**Decision:** Add the local package to root **`pyproject.toml`**, e.g. path dependency `{ path = "mcp_csv_server", develop = true }` (or the equivalent supported by your installer), so `app` can import `mcp_csv_server`.

Ensure **pandas** comes transitively from **`mcp_csv_server`**; verify lock/install in CI.

### 3. Intent: when to use the disaster path

**Decision:** Combine **lightweight signals** so most PDF questions stay on RAG:

- **Keyword / phrase cues** (e.g. disaster, EM-DAT, earthquake, flood, drought, cyclone, tsunami, volcanic, “natural disaster”, country + year-style questions clearly about **global disaster records**).
- Optional **negative cues** (e.g. “my resume”, “the uploaded PDF”) to prefer RAG when both could match.

If ambiguous, **default to existing RAG** (safer for unrelated uploads) unless configuration allows “prefer disaster when CSV domain is mentioned.”

**Optional refinement:** One **small structured LLM call** (same Anthropic key as today) that returns JSON `{ "use_disaster_tool": bool, "arguments": { ... } }` with a strict schema mirroring MCP args — use only when heuristics are insufficient; keep behind a setting if added.

### 4. Natural language → `query_natural_disasters` arguments

**Decision:** Prefer **structured extraction**:

- **Phase 1:** Regex / rules for **years** (ranges), **ISO-like** codes, and **country names** where feasible; map disaster-related **nouns** to `disaster_type` / `disaster_subgroup` substring filters.
- **Phase 2 (optional):** Haiku JSON mode (or tool-use) to fill `year_min`, `year_max`, `country`, `iso`, `disaster_type`, `disaster_subgroup`, `limit`, `datasets`, with validation via existing **`params_from_arguments`** / **`QueryParams`**.

Always **validate** through existing helpers so invalid combinations raise **clear errors** surfaced in the HTTP response (4xx) or as a user-visible message in `answer`, per existing API error style.

### 5. Response mapping

**Decision:** **`answer`** = tool output string (already includes match counts and markdown or plain table). **`sources`**: use **`[]`** or a **single synthetic** `SourceChunk` describing the EM-DAT CSV provenance (no fake “chunk” text from PDFs). Document the choice in OpenAPI descriptions if updated.

### 6. Configuration & failure modes

- **`ANTHROPIC_API_KEY`:** RAG path still requires it today. For **disaster-only** requests, decide whether to allow answers **without** LLM (tool output only). **Recommendation:** permit disaster path **without** invoking Claude if routing + args need no LLM — only require the key when falling back to RAG or when using an LLM for extraction.
- **Missing CSV files:** `run_query_from_loaded` can raise **`FileNotFoundError`** — map to **503** or **500** with a clear detail string.
- **Empty index:** Existing RAG returns a message when Chroma is empty; disaster path **should not** depend on Chroma count.

## Risks / Trade-offs

- **False positives:** Keywords route disaster queries incorrectly → wrong data or missed PDF answers. Mitigate with conservative keywords and optional LLM confirmation.
- **False negatives:** User asks about disasters in uploaded PDFs → RAG may answer instead of CSV. Mitigate with clearer product copy or future explicit `mode` parameter (out of scope unless requested).
