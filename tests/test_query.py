from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from app.main import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def test_query_missing_api_key_returns_503(client):
    with patch("app.routers.query.settings") as mock_settings:
        mock_settings.anthropic_api_key = None
        mock_settings.anthropic_model = "claude-haiku-4-5"
        r = client.post("/query", json={"question": "What is this?"})
    assert r.status_code == 503
    assert "ANTHROPIC_API_KEY" in r.json()["detail"]


def test_query_empty_store_short_circuits(client):
    mock_store = MagicMock()
    mock_store._collection.count.return_value = 0

    with patch("app.routers.query.settings") as mock_settings:
        mock_settings.anthropic_api_key = "sk-test"
        mock_settings.anthropic_model = "claude-haiku-4-5"
        with patch("app.services.query.get_vectorstore", return_value=mock_store):
            r = client.post("/query", json={"question": "Hello?"})
    assert r.status_code == 200
    data = r.json()
    assert "No documents have been indexed" in data["answer"]
    assert data["sources"] == []


def test_query_invokes_llm_with_grounding_context(client):
    mock_store = MagicMock()
    mock_store._collection.count.return_value = 2
    mock_store.similarity_search_with_score.return_value = [
        (Document(page_content="Alpha fact about widgets.", metadata={"page": 1}), 0.35),
        (Document(page_content="Beta detail.", metadata={"page": 2}), 0.42),
    ]

    captured_messages = None

    def fake_invoke(msgs):
        nonlocal captured_messages
        captured_messages = msgs
        return AIMessage(content="Widgets are described in the passages.")

    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = fake_invoke

    with patch("app.routers.query.settings") as mock_settings:
        mock_settings.anthropic_api_key = "sk-test"
        mock_settings.anthropic_model = "claude-haiku-4-5"
        mock_settings.query_dense_weak_best_distance_gt = 1.5
        mock_settings.query_lexical_min_alpha_tokens = 5
        mock_settings.query_lexical_enable_quotes = True
        mock_settings.query_lexical_enable_identifiers = True
        with patch("app.services.query.get_vectorstore", return_value=mock_store):
            with patch("app.services.query.ChatAnthropic", return_value=mock_llm):
                r = client.post(
                    "/query",
                    json={"question": "What about widgets?", "k": 4},
                )

    assert r.status_code == 200
    data = r.json()
    assert data["answer"] == "Widgets are described in the passages."
    assert len(data["sources"]) == 2
    assert "Alpha fact about widgets." in data["sources"][0]["content"]

    mock_store.similarity_search_with_score.assert_called_once_with(
        "What about widgets?", k=4
    )
    assert captured_messages is not None
    human = next(m for m in captured_messages if m.type == "human")
    assert "Alpha fact about widgets." in human.content
    assert "What about widgets?" in human.content
    system = next(m for m in captured_messages if m.type == "system")
    assert "ONLY" in system.content or "only" in system.content.lower()
