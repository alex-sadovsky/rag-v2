## Context

`app/services/rag.py` currently imports `HuggingFaceEmbeddings` from `langchain_community.embeddings`. LangChain 0.2.2 moved this class to a dedicated package (`langchain-huggingface`) and marked the community re-export as deprecated. The deprecation warning fires on the first `/upload` request when the lazy singleton `_get_embeddings()` is called.

## Goals / Non-Goals

**Goals:**
- Eliminate the `LangChainDeprecationWarning` at runtime
- Make `langchain-huggingface` an explicit direct dependency in `pyproject.toml`

**Non-Goals:**
- Changing embedding model, chunking strategy, or vector store
- Adding `HF_TOKEN` support (separate concern)
- Upgrading other LangChain packages

## Decisions

**Use `langchain-huggingface` directly, not a workaround**
The community package re-export will be removed in LangChain 1.0. Using the dedicated package is the officially recommended migration path. Suppressing the warning via `warnings.filterwarnings` would only hide the problem.

**Add to `pyproject.toml` as a direct dependency**
`langchain-huggingface` will no longer be pulled in transitively once `langchain_community` removes the re-export. Declaring it explicitly makes the dependency graph correct and prevents a future silent breakage.

## Risks / Trade-offs

- [Minor API drift] `langchain-huggingface` may have slightly different default kwargs than the community shim → No risk here: `model_name` is the only kwarg used and it is identical in both packages.
- [Transitive version conflict] `langchain-huggingface` may pin `transformers` or `sentence-transformers` differently → Low risk; both are already direct deps and the version constraints are compatible.
