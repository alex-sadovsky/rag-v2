"""Load EM-DAT-style disaster CSVs and run Pandas-only queries."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import pandas as pd

from mcp_csv_server.paths import get_disaster_csv_dir

FILE_1900 = "1900_2021_DISASTERS.xlsx - emdat data.csv"
FILE_1970 = "1970-2021_DISASTERS.xlsx - emdat data.csv"

DATASET_1900 = "1900-2021"
DATASET_1970 = "1970-2021"

DEFAULT_LIMIT = 50
MAX_LIMIT = 500
DEFAULT_MAX_CHARS = 100_000

DatasetsChoice = Literal["1900", "1970", "both"]

_cached_frame: pd.DataFrame | None = None
_cached_key: tuple[str, ...] | None = None


def reset_disaster_cache() -> None:
    """Clear the in-memory frame (for tests)."""
    global _cached_frame, _cached_key
    _cached_frame = None
    _cached_key = None


def _csv_paths() -> tuple[Path, Path]:
    base = get_disaster_csv_dir()
    p1900 = base / FILE_1900
    p1970 = base / FILE_1970
    return p1900, p1970


def _load_one(path: Path, dataset_label: str) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Disaster data file not found: {path}")
    df = pd.read_csv(path, low_memory=False)
    df["dataset"] = dataset_label
    return df


def load_combined_disasters() -> pd.DataFrame:
    """Load both CSVs, union columns, concat vertically, tag ``dataset`` column."""
    global _cached_frame, _cached_key
    p1900, p1970 = _csv_paths()
    key = (str(p1900.resolve()), str(p1970.resolve()), str(os.stat(p1900).st_mtime_ns), str(os.stat(p1970).st_mtime_ns))
    if _cached_frame is not None and _cached_key == key:
        return _cached_frame

    left = _load_one(p1900, DATASET_1900)
    right = _load_one(p1970, DATASET_1970)
    combined = pd.concat([left, right], axis=0, ignore_index=True, sort=False)
    _cached_frame = combined
    _cached_key = key
    return combined


@dataclass(frozen=True)
class QueryParams:
    datasets: DatasetsChoice = "both"
    year_min: int | None = None
    year_max: int | None = None
    country: str | None = None
    iso: str | None = None
    disaster_type: str | None = None
    disaster_subgroup: str | None = None
    limit: int = DEFAULT_LIMIT
    columns: list[str] | None = None
    sort_by: str | None = None
    ascending: bool = True
    max_chars: int = DEFAULT_MAX_CHARS


def _normalize_limit(raw: Any) -> int:
    if raw is None:
        return DEFAULT_LIMIT
    try:
        n = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("limit must be an integer") from exc
    if n < 1:
        return 1
    return min(n, MAX_LIMIT)


def _coerce_bool(raw: Any, default: bool) -> bool:
    if raw is None:
        return default
    if isinstance(raw, bool):
        return raw
    raise ValueError("ascending must be a boolean")


def params_from_arguments(arguments: dict[str, Any] | None) -> QueryParams:
    """Build QueryParams from MCP tool arguments; raises ValueError on bad input."""
    a = arguments or {}
    ds = a.get("datasets", "both")
    if ds not in ("1900", "1970", "both"):
        raise ValueError('datasets must be one of: "1900", "1970", "both"')

    cols = a.get("columns")
    if cols is not None and not isinstance(cols, list):
        raise ValueError("columns must be an array of strings")
    col_list = [str(c) for c in cols] if cols else None

    return QueryParams(
        datasets=ds,  # type: ignore[arg-type]
        year_min=_optional_int(a.get("year_min")),
        year_max=_optional_int(a.get("year_max")),
        country=_optional_str(a.get("country")),
        iso=_optional_str(a.get("iso")),
        disaster_type=_optional_str(a.get("disaster_type")),
        disaster_subgroup=_optional_str(a.get("disaster_subgroup")),
        limit=_normalize_limit(a.get("limit")),
        columns=col_list,
        sort_by=_optional_str(a.get("sort_by")),
        ascending=_coerce_bool(a.get("ascending"), True),
        max_chars=_normalize_max_chars(a.get("max_chars")),
    )


def _optional_int(v: Any) -> int | None:
    if v is None or v == "":
        return None
    try:
        return int(v)
    except (TypeError, ValueError) as exc:
        raise ValueError("year_min, year_max, and max_chars must be integers when provided") from exc


def _optional_str(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def _normalize_max_chars(raw: Any) -> int:
    if raw is None:
        return DEFAULT_MAX_CHARS
    n = _optional_int(raw)
    if n is None:
        return DEFAULT_MAX_CHARS
    return max(1_000, min(n, 500_000))


def query_natural_disasters(df: pd.DataFrame, params: QueryParams) -> str:
    """Filter, sort, limit, and format results as plain text / markdown."""
    if params.datasets == "1900":
        out = df[df["dataset"] == DATASET_1900].copy()
    elif params.datasets == "1970":
        out = df[df["dataset"] == DATASET_1970].copy()
    else:
        out = df.copy()

    if "Year" not in out.columns:
        raise ValueError("Combined data is missing required column 'Year'")

    if params.year_min is not None:
        out = out[out["Year"] >= params.year_min]
    if params.year_max is not None:
        out = out[out["Year"] <= params.year_max]

    if params.iso:
        if "ISO" not in out.columns:
            raise ValueError("Column 'ISO' not present in data")
        out = out[out["ISO"].astype(str).str.upper() == params.iso.upper()]

    if params.country:
        if "Country" not in out.columns:
            raise ValueError("Column 'Country' not present in data")
        mask = out["Country"].astype(str).str.contains(
            params.country, case=False, na=False, regex=False
        )
        out = out[mask]

    if params.disaster_type:
        col = "Disaster Type"
        if col not in out.columns:
            raise ValueError(f"Column {col!r} not present in data")
        mask = out[col].astype(str).str.contains(
            params.disaster_type, case=False, na=False, regex=False
        )
        out = out[mask]

    if params.disaster_subgroup:
        col = "Disaster Subgroup"
        if col not in out.columns:
            raise ValueError(f"Column {col!r} not present in data")
        mask = out[col].astype(str).str.contains(
            params.disaster_subgroup, case=False, na=False, regex=False
        )
        out = out[mask]

    if params.sort_by:
        if params.sort_by not in out.columns:
            raise ValueError(
                f"sort_by column {params.sort_by!r} not found. "
                f"Available (sample): {', '.join(sorted(out.columns.astype(str).tolist())[:40])}..."
            )
        out = out.sort_values(by=params.sort_by, ascending=params.ascending, na_position="last")

    total_matching = len(out)
    limited = out.head(params.limit)

    if params.columns:
        unknown = [c for c in params.columns if c not in limited.columns]
        if unknown:
            raise ValueError(f"Unknown columns requested: {unknown}")
        display = limited[params.columns]
    else:
        display = limited

    text = _format_result(display, total_matching, params.limit)
    if len(text) > params.max_chars:
        text = text[: params.max_chars] + (
            f"\n\n[Truncated output to {params.max_chars} characters; "
            "narrow filters, reduce limit, or use fewer columns.]"
        )
    return text


def _format_result(display: pd.DataFrame, total_matching: int, limit: int) -> str:
    n = len(display)
    head = (
        f"Natural disaster query: {total_matching} row(s) matched; "
        f"showing {n} (limit={limit}).\n"
        f"Filters use column Year; Country match is case-insensitive substring; "
        f"ISO is exact (case-insensitive).\n\n"
    )
    if n == 0:
        return head + "No rows matched."

    if n <= 25 and len(display.columns) <= 16:
        body = _markdown_table(display)
    else:
        body = display.to_string(index=False)
    return head + body


def _markdown_table(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    esc = lambda x: str(x).replace("|", "\\|")
    header = "| " + " | ".join(esc(c) for c in cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    rows = []
    for _, row in df.iterrows():
        cells = [esc(row[c]) for c in df.columns]
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep, *rows])


def run_query_from_loaded(arguments: dict[str, Any] | None) -> str:
    """Load (cached) data and run query; for MCP tool and tests."""
    params = params_from_arguments(arguments)
    df = load_combined_disasters()
    return query_natural_disasters(df, params)
