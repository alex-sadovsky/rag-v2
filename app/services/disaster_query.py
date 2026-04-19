"""Natural-disaster CSV branch for ``POST /query`` (same logic as MCP ``query_natural_disasters``)."""

from __future__ import annotations

import re
from typing import Any

from mcp_csv_server.disasters import params_from_arguments, run_query_from_loaded

from app.config import Settings

# Strong cues: user is asking about global EM-DAT-style tabular data, not uploaded PDFs.
_STRONG_CSV_HINTS: tuple[str, ...] = (
    "em-dat",
    "emdat",
    "natural disaster",
    "natural disasters",
    "disaster records",
    "disaster type",
    "disaster subgroup",
    "global disaster",
)

# Hazard terms — usually need an extra signal (year, country, impact wording) to route.
_DISASTER_TERMS: tuple[str, ...] = (
    "earthquake",
    "earthquakes",
    "flood",
    "floods",
    "drought",
    "droughts",
    "cyclone",
    "cyclones",
    "hurricane",
    "hurricanes",
    "typhoon",
    "typhoons",
    "tsunami",
    "tsunamis",
    "volcanic",
    "volcano",
    "volcanoes",
    "landslide",
    "landslides",
    "wildfire",
    "wildfires",
    "storm",
    "storms",
)

# Prefer RAG when the user is clearly asking about their own documents.
_RESUME_DOC_HINTS: tuple[str, ...] = (
    "my resume",
    "this resume",
    "my cv",
    "the uploaded pdf",
    "uploaded pdf",
    "indexed pdf",
    "from the pdf",
)

_YEAR_RE = re.compile(r"\b((?:19|20)\d{2})\b")
# Rough ISO-3166 alpha-3 pattern (exclude common English 3-letter words).
_ISO_BLOCKLIST = frozenset(
    {
        "AND",
        "THE",
        "FOR",
        "NOT",
        "BUT",
        "ARE",
        "WAS",
        "HAS",
        "HAD",
        "CAN",
        "MAY",
        "ALL",
        "OUR",
        "WHO",
        "HOW",
        "WHY",
        "ANY",
        "GET",
        "HIS",
        "HER",
        "ITS",
        "NOW",
        "NEW",
        "OLD",
        "OUT",
        "ONE",
        "TWO",
        "SIX",
        "TEN",
    }
)


def _extra_keywords_tuple(settings: Settings) -> tuple[str, ...]:
    raw = (settings.query_disaster_extra_keywords or "").strip()
    if not raw:
        return ()
    return tuple(s.strip().lower() for s in raw.split(",") if s.strip())


def is_natural_disaster_query(question: str, settings: Settings) -> bool:
    """Return True when the question should use EM-DAT CSV query instead of RAG."""
    if not settings.query_disaster_route_enabled:
        return False

    lower = question.lower()

    has_strong_csv_cue = any(s in lower for s in _STRONG_CSV_HINTS)
    if any(h in lower for h in _RESUME_DOC_HINTS) and not has_strong_csv_cue:
        return False

    extras = _extra_keywords_tuple(settings)
    if any(e in lower for e in extras):
        return True

    if any(s in lower for s in _STRONG_CSV_HINTS):
        return True

    if not any(t in lower for t in _DISASTER_TERMS):
        return False

    # Disaster term present: require an extra signal so vague questions stay on RAG.
    if _YEAR_RE.search(question):
        return True
    if "country" in lower or "countries" in lower:
        return True
    if "how many" in lower:
        return True
    if any(w in lower for w in ("killed", "deaths", "affected", "injured", "damages")):
        return True
    if _extract_iso(question):
        return True
    if _extract_country_phrase(lower):
        return True

    return False


def _extract_iso(question: str) -> str | None:
    # Avoid matching "DAT" inside "EM-DAT".
    scrubbed = re.sub(r"\bEM-?DAT\b", "emdat", question, flags=re.IGNORECASE)
    m = re.search(r"\b([A-Z]{3})\b", scrubbed)
    if not m:
        return None
    code = m.group(1)
    if code in _ISO_BLOCKLIST:
        return None
    return code


def _extract_country_phrase(lower: str) -> str | None:
    """Substring for ``Country`` column: phrase after 'in' / 'for' (limited length)."""
    m = re.search(
        r"\b(?:in|for)\s+(?:the\s+)?([a-z][a-z\s]{1,48}?)(?=\s+(?:in|during|from|between|and|or)\b|[?.,!]|$)",
        lower,
    )
    if not m:
        return None
    phrase = " ".join(m.group(1).split())
    if len(phrase) < 3:
        return None
    return phrase


def _first_disaster_type_token(lower: str) -> str | None:
    for t in _DISASTER_TERMS:
        if t in lower:
            # Use a stable singular-ish token for substring match on Disaster Type.
            return t.rstrip("s") if len(t) > 1 and t.endswith("s") else t
    return None


def question_to_disaster_arguments(question: str, settings: Settings) -> dict[str, Any]:
    """Map natural language to MCP ``query_natural_disasters`` argument dict (phase-1 heuristics)."""
    lower = question.lower()
    args: dict[str, Any] = {
        "datasets": "both",
        "limit": settings.query_disaster_default_limit,
    }

    years = [int(y) for y in _YEAR_RE.findall(question)]
    if years:
        args["year_min"] = min(years)
        args["year_max"] = max(years)

    iso = _extract_iso(question)
    if iso:
        args["iso"] = iso

    country = _extract_country_phrase(lower)
    if country and "iso" not in args:
        args["country"] = country

    dt = _first_disaster_type_token(lower)
    if dt:
        args["disaster_type"] = dt

    # Validate through the same parser the MCP tool uses.
    params_from_arguments(args)
    return args


def run_disaster_query(question: str, settings: Settings) -> str:
    """Execute the same query body as MCP ``query_natural_disasters``; raises MCP/data errors."""
    args = question_to_disaster_arguments(question, settings)
    return run_query_from_loaded(args)
