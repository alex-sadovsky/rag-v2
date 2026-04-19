"""Resolve repository paths for disaster CSV data."""

from __future__ import annotations

import os
from pathlib import Path

_ENV_CSV_DIR = "MCP_DISASTER_CSV_DIR"


def find_repo_root(start: Path | None = None) -> Path:
    """Walk parents until a directory contains ``dataset/csv``."""
    here = (start or Path(__file__)).resolve()
    for base in [here.parent, *here.parents]:
        if (base / "dataset" / "csv").is_dir():
            return base
    msg = (
        "Could not find repository root (no dataset/csv directory in parents of "
        f"{here}). Set {_ENV_CSV_DIR} to the directory containing the CSV files."
    )
    raise FileNotFoundError(msg)


def get_disaster_csv_dir() -> Path:
    """Directory containing EM-DAT CSV exports; override with MCP_DISASTER_CSV_DIR."""
    override = os.environ.get(_ENV_CSV_DIR)
    if override:
        return Path(override).expanduser().resolve()
    return find_repo_root() / "dataset" / "csv"
