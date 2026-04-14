#!/usr/bin/env python3
"""Run golden-dataset cases from golden_dataset.txt against POST /query.

Prerequisites:
  - API server running (e.g. ``python main.py``) with the same base URL as ``--base-url``.
  - Target PDFs already ingested via ``POST /upload`` in that server process (in-memory store).
  - ``ANTHROPIC_API_KEY`` set in the server environment so ``/query`` returns 200.

Example (from repo root)::

    .venv/bin/python scripts/run_golden_dataset.py
    .venv/bin/python scripts/run_golden_dataset.py --case directors-highlights
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urljoin


def default_dataset_path() -> Path:
    """``golden_dataset.txt`` at repository root (parent of ``scripts/``)."""
    return Path(__file__).resolve().parent.parent / "golden_dataset.txt"


def load_dataset(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict) or "cases" not in data:
        raise ValueError("dataset must be a JSON object with a 'cases' key")
    if not isinstance(data["cases"], list):
        raise ValueError("'cases' must be a list")
    return data


def resolve_k(case: dict[str, Any], defaults: dict[str, Any]) -> int:
    if "k" in case and case["k"] is not None:
        return int(case["k"])
    if "k" in defaults and defaults["k"] is not None:
        return int(defaults["k"])
    return 5


def check_answer(
    answer: str,
    must_contain: list[str],
    must_not_contain: list[str],
) -> list[str]:
    """Return human-readable failure reasons; empty list means pass."""
    reasons: list[str] = []
    lower = answer.lower()
    for needle in must_contain:
        if needle.lower() not in lower:
            reasons.append(f"missing must_contain: {needle!r}")
    for needle in must_not_contain:
        if needle.lower() in lower:
            reasons.append(f"found must_not_contain: {needle!r}")
    return reasons


def post_query(base_url: str, question: str, k: int, timeout: float) -> dict[str, Any]:
    url = urljoin(base_url.rstrip("/") + "/", "query")
    body = json.dumps({"question": question, "k": k}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = resp.read().decode("utf-8")
    return json.loads(payload)


def format_http_error(exc: BaseException, base_url: str) -> str:
    if isinstance(exc, urllib.error.HTTPError):
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(detail)
            inner = parsed.get("detail", parsed)
        except json.JSONDecodeError:
            inner = detail
        if exc.code == 503:
            return (
                f"HTTP {exc.code} from /query — is ANTHROPIC_API_KEY set on the server? "
                f"Detail: {inner!r}"
            )
        return f"HTTP {exc.code} from /query: {inner!r}"
    if isinstance(exc, urllib.error.URLError):
        reason = exc.reason
        msg = str(reason) if reason else str(exc)
        if "Connection refused" in msg or "actively refused" in msg.lower():
            return (
                f"Could not connect to {base_url!r}. Start the API (e.g. python main.py) "
                "and ingest PDFs before running this script."
            )
        return f"Request failed: {msg}"
    return str(exc)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate RAG answers using golden_dataset.txt and POST /query.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="API root (default: %(default)s)",
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=default_dataset_path(),
        help="Path to golden_dataset JSON file (default: repo root golden_dataset.txt)",
    )
    parser.add_argument(
        "--case",
        action="append",
        dest="case_ids",
        metavar="ID",
        help="Run only case(s) with this id (repeatable)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="HTTP timeout in seconds for each /query call (default: %(default)s)",
    )
    args = parser.parse_args(argv)

    try:
        data = load_dataset(args.dataset)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"Failed to load dataset {args.dataset}: {e}", file=sys.stderr)
        return 1

    defaults = data.get("defaults") or {}
    if not isinstance(defaults, dict):
        print("'defaults' must be an object when present", file=sys.stderr)
        return 1

    cases_raw = data["cases"]
    cases: list[dict[str, Any]] = [c for c in cases_raw if isinstance(c, dict)]
    if args.case_ids:
        want = set(args.case_ids)
        cases = [c for c in cases if c.get("id") in want]
        missing = want - {c.get("id") for c in cases}
        if missing:
            print(f"Unknown case id(s): {sorted(missing)}", file=sys.stderr)
            return 1

    if not cases:
        print("No cases to run.", file=sys.stderr)
        return 1

    any_fail = False
    for case in cases:
        cid = case.get("id", "?")
        question = case.get("question")
        if not question or not isinstance(question, str):
            print(f"[{cid}] FAIL: missing question", file=sys.stderr)
            any_fail = True
            continue

        k = resolve_k(case, defaults)
        must_contain = case.get("must_contain") or []
        must_not_contain = case.get("must_not_contain") or []
        if not isinstance(must_contain, list):
            must_contain = []
        if not isinstance(must_not_contain, list):
            must_not_contain = []
        must_contain_s = [str(x) for x in must_contain]
        must_not_contain_s = [str(x) for x in must_not_contain]

        try:
            resp = post_query(args.base_url, question.strip(), k, args.timeout)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"[{cid}] FAIL: {format_http_error(e, args.base_url)}", file=sys.stderr)
            any_fail = True
            continue
        except json.JSONDecodeError as e:
            print(f"[{cid}] FAIL: invalid JSON from /query: {e}", file=sys.stderr)
            any_fail = True
            continue

        if not isinstance(resp, dict) or "answer" not in resp:
            print(f"[{cid}] FAIL: response missing 'answer' key: {resp!r}", file=sys.stderr)
            any_fail = True
            continue

        answer = resp.get("answer")
        if not isinstance(answer, str):
            print(f"[{cid}] FAIL: 'answer' is not a string", file=sys.stderr)
            any_fail = True
            continue

        reasons = check_answer(answer, must_contain_s, must_not_contain_s)
        if reasons:
            any_fail = True
            print(f"[{cid}] FAIL: " + "; ".join(reasons))
        else:
            print(f"[{cid}] PASS")

    return 1 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
