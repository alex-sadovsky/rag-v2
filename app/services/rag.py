from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.hybrid_retrieval import invalidate_hybrid_index

_embeddings: HuggingFaceEmbeddings | None = None
_vectorstore: Chroma | None = None
_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)


def _get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return _embeddings


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(embedding_function=_get_embeddings())
    return _vectorstore


def ingest_pdf(path: Path) -> int:
    docs = PyPDFLoader(str(path)).load()
    chunks = _splitter.split_documents(docs)
    get_vectorstore().add_documents(chunks)
    invalidate_hybrid_index()
    return len(chunks)
