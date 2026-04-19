"""Unit tests for disaster query logic (synthetic DataFrames)."""

import pandas as pd
import pytest

from mcp_csv_server.disasters import (
    DATASET_1900,
    DATASET_1970,
    QueryParams,
    params_from_arguments,
    query_natural_disasters,
    reset_disaster_cache,
)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    reset_disaster_cache()
    yield
    reset_disaster_cache()


def _sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "dataset": [DATASET_1900, DATASET_1970, DATASET_1900],
            "Year": [2000, 2001, 1999],
            "Country": ["India", "United States", "India"],
            "ISO": ["IND", "USA", "IND"],
            "Disaster Type": ["Flood", "Storm", "Drought"],
            "Disaster Subgroup": ["Hydrological", "Meteorological", "Climatological"],
        }
    )


def test_params_from_arguments_defaults() -> None:
    p = params_from_arguments({})
    assert p.datasets == "both"
    assert p.limit == 50


def test_params_invalid_datasets() -> None:
    with pytest.raises(ValueError, match="datasets"):
        params_from_arguments({"datasets": "all"})


def test_query_year_and_country() -> None:
    df = _sample_frame()
    p = QueryParams(year_min=2000, year_max=2001, country="united", limit=10)
    text = query_natural_disasters(df, p)
    assert "1 row" in text or "1 row(s)" in text
    assert "United States" in text


def test_query_iso_and_dataset_filter() -> None:
    df = _sample_frame()
    p = QueryParams(datasets="1900", iso="IND", limit=10)
    text = query_natural_disasters(df, p)
    assert "2 row" in text or "2 row(s)" in text


def test_unknown_column_in_sort_errors() -> None:
    df = _sample_frame()
    p = QueryParams(sort_by="Nope", limit=5)
    with pytest.raises(ValueError, match="sort_by"):
        query_natural_disasters(df, p)


def test_unknown_requested_columns() -> None:
    df = _sample_frame()
    p = QueryParams(columns=["Year", "NotThere"], limit=5)
    with pytest.raises(ValueError, match="Unknown columns"):
        query_natural_disasters(df, p)
