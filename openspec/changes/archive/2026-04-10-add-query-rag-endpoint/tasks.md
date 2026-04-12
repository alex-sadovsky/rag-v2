## 1. Dependencies and configuration

- [x] 1.1 Add `langchain-anthropic` to `pyproject.toml` (version compatible with existing `langchain` stack)
- [x] 1.2 Extend `app/config.py` with `anthropic_api_key` and `anthropic_model` (default `claude-haiku-4-5`), loaded from `ANTHROPIC_API_KEY` / `ANTHROPIC_MODEL`
- [x] 1.3 Install dependencies into the project environment

## 2. RAG query service

- [x] 2.1 Add a function (e.g. in `app/services/rag.py` or `app/services/query.py`) that takes a question string, calls `get_vectorstore().similarity_search` (or with scores), and assembles a fixed **grounding** prompt with labeled context blocks
- [x] 2.2 Invoke Claude Haiku 4.5 via `ChatAnthropic` using settings for API key and model id
- [x] 2.3 Handle missing API key and empty store / empty retrieval with clear behavior (documented errors or messages)
- [x] 2.4 Optionally return structured fields: answer text + optional list of source snippets or metadata for debugging

## 3. HTTP API

- [x] 3.1 Add a FastAPI route `POST /query` with a Pydantic request model (`question: str`, optional `k` or similar with validation)
- [x] 3.2 Register the new router in `app/routers/__init__.py` without changing `app/main.py` (follow existing router pattern)
- [x] 3.3 Ensure OpenAPI docs describe the endpoint and error cases

## 4. Verification

- [x] 4.1 Add unit tests with mocked Chroma / `ChatAnthropic` to verify retrieval is invoked and the grounding prompt contains chunk text
- [x] 4.2 Manual check: upload a PDF, then `POST /query` with a question answerable from the text; confirm grounded response when `ANTHROPIC_API_KEY` is set (automated coverage in `tests/test_query.py`; optional live smoke test with a real key)
