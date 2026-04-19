## Why

The API exposes `POST /query` for grounded answers over indexed PDFs (and EM-DAT-style disaster questions), but interacting with it requires `curl` or an external client. A small browser UI lets developers and demos ask questions, read answers, and inspect sources without leaving the running app—consistent with how **`/analytics`** and **`/visualize`** already serve static HTML from `app/static/`.

## What Changes

- New static page under **`app/static/`** (same visual language as **`analytics.html`** / **`visualize.html`**: dark shell, system font, accent colors, status line).
- Client-side **`fetch`** to **`POST /query`** with JSON `{"question": "...", "k": N}` (default **k** aligned with API defaults).
- Conversation-style layout: user messages and assistant replies in a scrollable thread; optional display of **`sources`** from **`QueryResponse`** (collapsible or secondary panel) for transparency.
- Register a **GET** shortcut in **`app/main.py`** (e.g. **`/chat`**) that returns **`FileResponse`** for the new HTML file, mirroring **`/analytics`** and **`/visualize`** (`include_in_schema=False`).

## Capabilities

### Modified Capabilities

- **Developer / demo UX**: One-click access to the RAG (and disaster-branch) query flow from the same origin as the API—no new backend contract beyond existing `POST /query`.

## Impact

- `app/static/` — new HTML (and inline CSS/JS, consistent with sibling pages).
- `app/main.py` — one new route serving that file.
- No change to `POST /query` request/response models unless a follow-up adds optional fields (not required for this UI).
