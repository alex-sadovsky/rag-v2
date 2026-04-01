## 1. Dependencies

- [x] 1.1 Add `langchain`, `langchain-community`, `langchain-chroma`, `sentence-transformers`, `pypdf`, `chromadb` to `pyproject.toml`
- [x] 1.2 Install new dependencies into the venv

## 2. RAG Service

- [x] 2.1 Create `app/services/__init__.py`
- [x] 2.2 Create `app/services/rag.py` with module-level `_embeddings` singleton (`HuggingFaceEmbeddings`, model `sentence-transformers/all-MiniLM-L6-v2`)
- [x] 2.3 Add `_vectorstore` singleton and `get_vectorstore()` lazy initialiser in `app/services/rag.py`
- [x] 2.4 Implement `RecursiveCharacterTextSplitter` with `chunk_size=1000, chunk_overlap=0`
- [x] 2.5 Implement `ingest_pdf(path: Path) -> int` — loads with `PyPDFLoader`, splits, adds to vectorstore, returns chunk count

## 3. Upload Router Integration

- [x] 3.1 Import `ingest_pdf` in `app/routers/upload.py`
- [x] 3.2 Call `ingest_pdf(destination)` after saving the file
- [x] 3.3 Include `chunks` count in the response: `{"filename": ..., "chunks": N}`

## 4. Verification

- [x] 4.1 Upload a real PDF and verify HTTP 200 with `chunks` > 0 in the response
- [x] 4.2 Upload a second PDF and verify both are accepted (store accumulates)
