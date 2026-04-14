from langchain_core.documents import Document

from app.config import Settings
from app.services.rag import split_pages_hierarchically


def test_split_pages_hierarchically_sets_child_metadata():
    settings = Settings(
        rag_child_chunk_size=100,
        rag_child_chunk_overlap=0,
    )
    parent_body = "a" * 250
    pages = [
        Document(
            page_content=parent_body,
            metadata={"source": "/tmp/x.pdf", "page": 0},
        )
    ]
    children = split_pages_hierarchically(pages, settings)
    assert len(children) >= 2
    for idx, child in enumerate(children):
        assert child.metadata.get("hierarchy") == "child"
        assert child.metadata.get("child_index") == idx
        assert child.metadata.get("parent_page_content") == parent_body
        assert child.metadata.get("page") == 0
        assert child.metadata.get("source") == "/tmp/x.pdf"


def test_split_pages_hierarchically_indexes_children_per_page():
    settings = Settings(rag_child_chunk_size=100, rag_child_chunk_overlap=0)
    pages = [
        Document(page_content="p0 " + "x" * 220, metadata={"source": "a.pdf", "page": 0}),
        Document(page_content="p1 " + "y" * 220, metadata={"source": "a.pdf", "page": 1}),
    ]
    children = split_pages_hierarchically(pages, settings)
    by_page: dict[int, list[Document]] = {}
    for c in children:
        p = int(c.metadata["page"])
        by_page.setdefault(p, []).append(c)
    for p, group in by_page.items():
        for idx, child in enumerate(group):
            assert child.metadata["child_index"] == idx
            assert ("p0" in child.metadata["parent_page_content"]) == (p == 0)
            assert ("p1" in child.metadata["parent_page_content"]) == (p == 1)
