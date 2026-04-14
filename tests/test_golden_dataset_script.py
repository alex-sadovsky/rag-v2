"""Unit tests for scripts/run_golden_dataset.py (pure helpers, no HTTP)."""

import importlib.util
import json
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = _ROOT / "scripts" / "run_golden_dataset.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("run_golden_dataset", _SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gds():
    return _load_script()


def test_check_answer_passes_when_constraints_satisfied(gds):
    assert gds.check_answer(
        "VMware and Director roles are listed.",
        must_contain=["VMware", "Director"],
        must_not_contain=["Team of the Month"],
    ) == []


def test_check_answer_must_contain_failure(gds):
    reasons = gds.check_answer(
        "Only Director here.",
        must_contain=["VMware"],
        must_not_contain=[],
    )
    assert len(reasons) == 1
    assert "must_contain" in reasons[0]


def test_check_answer_must_not_contain_failure(gds):
    reasons = gds.check_answer(
        "Mentioned Team of the Month award.",
        must_contain=[],
        must_not_contain=["Team of the Month"],
    )
    assert len(reasons) == 1
    assert "must_not_contain" in reasons[0]


def test_check_answer_case_insensitive(gds):
    assert gds.check_answer(
        "vmware is great",
        must_contain=["VmWaRe"],
        must_not_contain=[],
    ) == []


def test_resolve_k_and_load_dataset(gds, tmp_path):
    p = tmp_path / "g.json"
    p.write_text(
        json.dumps(
            {
                "defaults": {"k": 3},
                "cases": [{"id": "a", "question": "q"}],
            }
        ),
        encoding="utf-8",
    )
    data = gds.load_dataset(p)
    assert data["cases"][0]["id"] == "a"
    assert gds.resolve_k(data["cases"][0], data["defaults"]) == 3

    p2 = tmp_path / "bad.json"
    p2.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="cases"):
        gds.load_dataset(p2)
