from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

from app.config import Settings
from app.services import hybrid_retrieval as hr


@pytest.fixture
def settings_tight_weak() -> Settings:
    """Weak dense when best distance > 0.5 (easy to trigger in tests)."""
    return Settings(
        query_dense_weak_best_distance_gt=0.5,
        anthropic_api_key="sk-test",
    )


@pytest.fixture
def settings_never_weak() -> Settings:
    """Weak only when distance > 2.0 (typical good matches stay below)."""
    return Settings(
        query_dense_weak_best_distance_gt=2.0,
        anthropic_api_key="sk-test",
    )


def test_weak_dense_signal_true_when_best_above_threshold(settings_tight_weak):
    assert hr.weak_dense_signal([0.9, 1.2, 1.0], settings_tight_weak) is True


def test_weak_dense_signal_false_when_best_below_threshold(settings_tight_weak):
    assert hr.weak_dense_signal([0.2, 0.8], settings_tight_weak) is False


def test_lexical_quoted_phrase():
    s = Settings(anthropic_api_key="sk-test")
    assert hr.lexical_warranted('What does "Foo Bar" mean?', s) is True


def test_lexical_acronym_and_digit():
    s = Settings(anthropic_api_key="sk-test")
    assert hr.lexical_warranted("Explain the API v2 for RAG", s) is True


def test_lexical_hyphen_identifier():
    s = Settings(anthropic_api_key="sk-test")
    assert hr.lexical_warranted("What is cross-encoder ranking?", s) is True


def test_lexical_min_tokens_only():
    s = Settings(anthropic_api_key="sk-test", query_lexical_min_alpha_tokens=4)
    assert hr.lexical_warranted(
        "widgets performance benchmarks datasets evaluation metrics", s
    ) is True


def test_lexical_short_generic_question():
    s = Settings(anthropic_api_key="sk-test", query_lexical_min_alpha_tokens=8)
    assert hr.lexical_warranted("What is it about?", s) is False


def test_fuse_dense_first_dedupes_and_caps():
    a = Document(page_content="same", metadata={"source": "x.pdf", "page": 1})
    b = Document(page_content="other", metadata={"source": "x.pdf", "page": 2})
    c = Document(page_content="third", metadata={"source": "y.pdf", "page": 1})
    fused = hr.fuse_dense_first([a, b], [a, c], k=2)
    assert len(fused) == 2
    assert fused[0].page_content == "same"
    assert fused[1].page_content == "other"


def test_retrieve_conditional_skips_bm25_when_dense_strong(settings_never_weak):
    store = MagicMock()
    store.similarity_search_with_score.return_value = [
        (Document(page_content="A", metadata={}), 0.3),
        (Document(page_content="B", metadata={}), 0.4),
    ]
    with patch.object(hr, "bm25_top_k") as bm25_mock:
        docs, used = hr.retrieve_chunks_conditional(
            '"quoted" heavy query',
            k=2,
            store=store,
            settings=settings_never_weak,
        )
    bm25_mock.assert_not_called()
    assert used is False
    assert [d.page_content for d in docs] == ["A", "B"]


def test_retrieve_conditional_calls_bm25_when_weak_and_lexical(settings_tight_weak):
    store = MagicMock()
    d1 = Document(page_content="A", metadata={})
    d2 = Document(page_content="B", metadata={})
    store.similarity_search_with_score.return_value = [(d1, 0.9), (d2, 1.0)]

    def fake_bm25(q, st, k):
        return [Document(page_content="C", metadata={"extra": True})]

    with patch.object(hr, "bm25_top_k", side_effect=fake_bm25):
        docs, used = hr.retrieve_chunks_conditional(
            'What is "Zebra" identifier X12?',
            k=2,
            store=store,
            settings=settings_tight_weak,
        )
    assert used is True
    assert len(docs) <= 2
