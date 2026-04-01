## Why

`HuggingFaceEmbeddings` imported from `langchain_community.embeddings` is deprecated since LangChain 0.2.2 and will be removed in LangChain 1.0. This triggers a `LangChainDeprecationWarning` on every first request to `/upload`, and the fix is straightforward — migrate to the dedicated `langchain-huggingface` package now before the class is removed.

## What Changes

- Replace `from langchain_community.embeddings import HuggingFaceEmbeddings` with `from langchain_huggingface import HuggingFaceEmbeddings` in `app/services/rag.py`
- Add `langchain-huggingface>=0.1.0` to `pyproject.toml` dependencies

## Capabilities

### New Capabilities
<!-- None — this is a dependency migration with no new user-facing behaviour -->

### Modified Capabilities
- `pdf-upload`: The embeddings backend used during ingestion changes packages; runtime behaviour is identical but the deprecation warning is eliminated.

## Impact

- **Code**: `app/services/rag.py` (one import line)
- **Dependencies**: `pyproject.toml` — new direct dependency on `langchain-huggingface`
- **APIs**: None — no endpoint signatures or response shapes change
- **Breaking**: None
