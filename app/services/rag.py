from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import Settings, settings as default_settings
from app.services.hybrid_retrieval import invalidate_hybrid_index

_embeddings: HuggingFaceEmbeddings | None = None
_vectorstore: Chroma | None = None


def split_pages_hierarchically(page_docs: list[Document], settings: Settings) -> list[Document]:
    """Split each page document into child chunks; attach hierarchy metadata for grounding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.rag_child_chunk_size,
        chunk_overlap=settings.rag_child_chunk_overlap,
    )
    out: list[Document] = []
    for page_doc in page_docs:
        parent_text = page_doc.page_content or ""
        children = splitter.split_documents([page_doc])
        for j, child in enumerate(children):
            md = dict(child.metadata) if child.metadata else {}
            md["hierarchy"] = "child"
            md["child_index"] = j
            md["parent_page_content"] = parent_text
            child.metadata = md
            out.append(child)
    return out


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


def ingest_pdf(path: Path, *, settings: Settings | None = None) -> int:
    cfg = settings if settings is not None else default_settings
    docs = PyPDFLoader(str(path)).load()
    chunks = split_pages_hierarchically(docs, cfg)
    get_vectorstore().add_documents(chunks)
    invalidate_hybrid_index()
    return len(chunks)
