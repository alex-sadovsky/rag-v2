## Context

- **`POST /query`** is implemented in `app/routers/query.py`; responses are **`QueryResponse`** with **`answer: str`** and **`sources: list[{ content, metadata }]`**.
- Static demos **`/analytics`** and **`/visualize`** are registered in **`app/main.py`** and load **`app/static/analytics.html`** and **`visualize.html`**. They use a shared aesthetic: **`#0f1117`** background, **`#1a1d27`** panels/headers, borders **`#2e3147`**, accents (**green** for analytics title, **purple** for visualize).
- The new page should feel like a third sibling: same typography (`system-ui`), layout discipline, and a **`#status`** line for loading/errors.

## Goals / Non-Goals

**Goals:**

- **Same-origin** `fetch` to **`/query`** (relative URL) so it works when the app is opened at `http://127.0.0.1:8000/chat` (or whatever host/port).
- **Chat thread UX**: show alternating user questions and assistant answers; scroll the transcript; keep an input + submit (and optionally Enter-to-send).
- **Optional `k`**: small numeric control (1–20) with default **5**, matching API validation.
- **Sources**: show **`sources`** in a readable way (e.g. expandable “Sources” under each assistant message, or a dedicated panel)—truncate long `content` with “show more” if needed, but keep first implementation simple.
- **Errors**: map **400** / **503** (and network failures) to clear **`#status`** or inline error styling (reuse **`.error`** pattern from **`analytics.html`**).

**Non-Goals:**

- **SSE / streaming** responses (API returns a full JSON body today).
- **Authentication** or multi-user sessions (single-browser demo only).
- **New API routes** beyond serving the HTML file; the UI consumes existing **`POST /query`** only.

## Decisions

### Page path and filename

- **GET `/chat`** → **`app/static/chat.html`** (or **`query.html`** if you prefer the name “query” in the URL—proposal uses **`/chat`** to avoid mentally overloading the **`/query`** name with GET vs POST). Implementation should pick one pair and document it in **`README.md`** in a single line if other static shortcuts are documented there.

### Styling

- Reuse the **header + main + status** structure from **`analytics.html`**: full-height flex column, bordered panels, uppercase section labels where helpful.
- Use a distinct accent for the chat page (e.g. **`#38bdf8`** sky or **`#a78bfa`** purple) for the `<h1>` to differentiate from analytics/visualize while staying on-palette.

### JavaScript behavior

- On submit: disable button briefly, set status to loading, **`POST`** with **`Content-Type: application/json`**.
- On success: append user bubble + assistant bubble; clear input; reset status to neutral or “Ready”.
- On error: parse **`detail`** from FastAPI JSON when present; show in status or under the last message.

### CORS

- Not required: page is served from the same app origin as **`/query`**.

## Risks / Trade-offs

- **503** when **`ANTHROPIC_API_KEY`** is missing for normal RAG questions—the UI must surface the server **`detail`** string clearly; disaster-only questions may still succeed without the key.
- Large **`sources`** payloads could dominate the DOM—start with simple blocks and optional collapse.
