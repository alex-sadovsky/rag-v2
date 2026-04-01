## Context

PDFs are currently saved to `uploads/` but their content is inaccessible for semantic search. This change introduces a RAG ingestion pipeline that runs synchronously inside `POST /upload`, using LangChain + Chroma + HuggingFace embeddings. The vector store lives in memory for the application lifetime.

## Goals / Non-Goals

**Goals:**
- Parse, chunk, embed, and index each uploaded PDF immediately after it is saved
- Return chunk count to the caller alongside the filename
- Keep the vector store as a module-level singleton accessible across requests
- Use `all-MiniLM-L6-v2` via `HuggingFaceEmbeddings` for embeddings
- Use Chroma in-memory mode (no disk persistence)

**Non-Goals:**
- Query/search endpoint (out of scope for this change)
- Async/background processing
- Persisting the vector store across app restarts
- Re-ingesting or deduplicating already-indexed documents
- Multi-document chunking strategies beyond `RecursiveCharacterTextSplitter`

## Decisions

### Pipeline location: `app/services/rag.py`
A dedicated services module keeps ingestion logic decoupled from the router. The router stays thin: save file, call `ingest_pdf(path)`, return response.

**Alternatives considered:**
- Inline in `upload.py`: mixes I/O and ML concerns, harder to test in isolation

### Vector store: Chroma in-memory singleton
`Chroma` is instantiated once at module level (lazy, on first call to `get_vectorstore()`). All requests share the same instance. Resets on app restart.

```
app/services/rag.py
  _vectorstore: Chroma | None = None

  def get_vectorstore() -> Chroma:
      global _vectorstore
      if _vectorstore is None:
          _vectorstore = Chroma(embedding_function=_embeddings())
      return _vectorstore

  def ingest_pdf(path: Path) -> int:
      docs = PyPDFLoader(str(path)).load()
      chunks = splitter.split_documents(docs)
      get_vectorstore().add_documents(chunks)
      return len(chunks)
```

**Alternatives considered:**
- Chroma persistent client: survives restarts but adds `chroma_dir` config and file I/O — out of scope
- Per-request Chroma: loses all prior embeddings between calls

### Embeddings: HuggingFaceEmbeddings (lazy singleton)
`HuggingFaceEmbeddings` is also held as a module-level singleton. Model is downloaded on first use (~90 MB) and cached by `sentence-transformers` in `~/.cache/`.

### Chunk size: 1000 characters, no overlap
`RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)` as specified. Overlap can be added later if retrieval quality needs improvement.

### Pipeline is synchronous
`ingest_pdf()` blocks until all chunks are embedded and added to Chroma. The caller (upload endpoint) waits. Acceptable for local development with small PDFs.

## Risks / Trade-offs

- **First-request latency** → Model downloads ~90 MB and loads into memory on first call. Mitigated by documenting this behavior; optionally pre-warm at startup.
- **Memory growth** → In-memory Chroma grows with every uploaded PDF, unbounded. Acceptable for local dev; would need eviction or persistence strategy for production.
- **No deduplication** → Re-uploading the same file adds duplicate chunks to the vector store. Acceptable for now.
- **Synchronous blocking** → Large PDFs with many chunks will slow the upload response. Acceptable for 5 MB limit and local use.
