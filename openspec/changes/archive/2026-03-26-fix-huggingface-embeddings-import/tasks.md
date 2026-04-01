## 1. Dependency

- [x] 1.1 Add `langchain-huggingface>=0.1.0` to the `dependencies` list in `pyproject.toml`
- [x] 1.2 Install the new package in the virtual environment: `.venv/bin/pip install -e .`

## 2. Code Change

- [x] 2.1 In `app/services/rag.py`, replace `from langchain_community.embeddings import HuggingFaceEmbeddings` with `from langchain_huggingface import HuggingFaceEmbeddings`

## 3. Verification

- [x] 3.1 Run `.venv/bin/python -W error::DeprecationWarning -c "from langchain_huggingface import HuggingFaceEmbeddings"` and confirm no warnings
- [x] 3.2 Start the app with `.venv/bin/python main.py` and confirm no `LangChainDeprecationWarning` appears in the logs on startup or first upload
