## 1. Static chat page

- [x] 1.1 Add **`app/static/chat.html`** (single-file HTML + CSS + JS) matching the look-and-feel of **`analytics.html`** / **`visualize.html`** (dark theme, header, status line, readable typography).
- [x] 1.2 Implement **`fetch('/query', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question, k }) })`** with validated **`k`** (integer 1–20, default **5**).
- [x] 1.3 Render a **message list**: user prompts and assistant **`answer`** text; append new pairs after each successful response.
- [x] 1.4 Render **`sources`**: show each source’s **`content`** (and optionally **`metadata`** summary) under the assistant message—collapsible section or secondary panel is acceptable.
- [x] 1.5 Handle **non-OK** responses: read JSON **`detail`** when available; show errors in **`#status`** (and/or inline) using the existing **`.error`** styling pattern.

## 2. Route registration

- [x] 2.1 In **`app/main.py`**, add **`@application.get("/chat", include_in_schema=False)`** (or the chosen path from design) returning **`FileResponse`** for the new HTML file, consistent with **`/analytics`** and **`/visualize`**.

## 3. Documentation (light touch)

- [x] 3.1 Add a short bullet or sentence to **`README.md`** in the **`/query`** section (or “Development / UI” if more appropriate) listing the new URL (e.g. **`/chat`**) so users discover the page.

## 4. Verification

- [x] 4.1 Manual: run the app, open **`/chat`**, send a question; confirm **`answer`** appears and **sources** render when returned.
- [x] 4.2 Manual: with **`ANTHROPIC_API_KEY`** unset, confirm a normal document question shows a clear **503** message via the UI; optionally verify a disaster-routed question still returns **200** if applicable in your environment.
