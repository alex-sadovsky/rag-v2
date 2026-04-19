"""Tests for natural-disaster routing and NL→tool-args heuristics."""

import pytest

from app.config import Settings
from app.services.disaster_query import (
    is_natural_disaster_query,
    question_to_disaster_arguments,
)


@pytest.fixture
def settings() -> Settings:
    return Settings()


def test_strong_cue_emdat(settings: Settings) -> None:
    assert is_natural_disaster_query("List EM-DAT earthquakes after 2000", settings) is True


def test_disaster_term_plus_year(settings: Settings) -> None:
    assert is_natural_disaster_query("How many floods occurred in 2015?", settings) is True


def test_resume_and_flood_prefers_rag(settings: Settings) -> None:
    assert (
        is_natural_disaster_query(
            "Does my resume mention flood risk experience?",
            settings,
        )
        is False
    )


def test_generic_widget_question_not_disaster(settings: Settings) -> None:
    assert is_natural_disaster_query("What about widgets in the PDF?", settings) is False


def test_emdat_overrides_resume_hint(settings: Settings) -> None:
    assert (
        is_natural_disaster_query(
            "Compare EM-DAT floods to the floods mentioned on my resume",
            settings,
        )
        is True
    )


def test_question_to_args_passes_params_from_arguments(settings: Settings) -> None:
    q = "EM-DAT drought in USA between 1999 and 2001"
    args = question_to_disaster_arguments(q, settings)
    assert args["datasets"] == "both"
    assert args["year_min"] == 1999
    assert args["year_max"] == 2001
    assert args["iso"] == "USA"
    assert args["disaster_type"] == "drought"


def test_extra_keywords_from_settings(settings: Settings) -> None:
    s = settings.model_copy(update={"query_disaster_extra_keywords": "kaggle, emdat"})
    assert is_natural_disaster_query("Show kaggle stats for anything", s) is True
