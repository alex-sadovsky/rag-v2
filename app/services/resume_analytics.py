"""Resume analytics from extracted PDF text on disk.

This module must not import Chroma, embeddings, or ``app.services.vectors`` —
statistics are derived only from plain text read via PyPDFLoader.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from pydantic import BaseModel, Field

from app.config import settings

# Longest phrases first (matched before shorter substrings).
_HEADING_RULES: list[tuple[str, str]] = [
    ("professional experience", "experience"),
    ("relevant experience", "experience"),
    ("employment history", "experience"),
    ("work experience", "experience"),
    ("work history", "experience"),
    ("academic background", "education"),
    ("technical skills", "skills"),
    ("core competencies", "skills"),
    ("selected projects", "projects"),
    ("certifications", "certifications"),
    ("qualifications", "education"),
    ("technologies", "skills"),
    ("certificates", "certifications"),
    ("employment", "experience"),
    ("experience", "experience"),
    ("education", "education"),
    ("university", "education"),
    ("objective", "summary"),
    ("overview", "summary"),
    ("about me", "summary"),
    ("projects", "projects"),
    ("portfolio", "projects"),
    ("summary", "summary"),
    ("profile", "summary"),
    ("skills", "skills"),
    ("expertise", "skills"),
    ("academic", "education"),
    ("career", "experience"),
]
_HEADING_RULES.sort(key=lambda x: len(x[0]), reverse=True)

_CATEGORY_LABELS: dict[str, str] = {
    "experience": "Experience",
    "education": "Education",
    "skills": "Skills",
    "summary": "Summary",
    "projects": "Projects",
    "certifications": "Certifications",
    "other": "Other",
}

_LEXICON_PATH = Path(__file__).resolve().parent.parent / "data" / "skills_lexicon.txt"
_lexicon_cache: list[str] | None = None


def _load_skills_lexicon() -> list[str]:
    global _lexicon_cache
    if _lexicon_cache is not None:
        return _lexicon_cache
    if not _LEXICON_PATH.is_file():
        _lexicon_cache = []
        return _lexicon_cache
    seen: set[str] = set()
    lines: list[str] = []
    for raw in _LEXICON_PATH.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s:
            continue
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        lines.append(s)
    lines.sort(key=len, reverse=True)
    _lexicon_cache = lines
    return _lexicon_cache


def _classify_heading(line: str) -> str | None:
    s = re.sub(r"^[\s#•\-\*]+", "", line.strip()).lower().rstrip(":").strip()
    if not s or len(s) > 72:
        return None
    for phrase, cat in _HEADING_RULES:
        if s == phrase:
            return cat
        if s.startswith(phrase + " ") or s.startswith(phrase + ":"):
            return cat
        if len(phrase) >= 12 and phrase in s and len(s) <= len(phrase) + 12:
            return cat
    return None


def _section_char_counts(text: str) -> dict[str, int]:
    """Assign each non-heading line to the current section; return char counts per category."""
    current = "other"
    buckets: dict[str, list[str]] = defaultdict(list)
    for line in text.splitlines():
        heading = _classify_heading(line)
        if heading is not None:
            current = heading
        else:
            buckets[current].append(line)
    return {k: len("\n".join(v)) for k, v in buckets.items()}


def _find_skills_in_text(text: str, lexicon: list[str]) -> set[str]:
    """Non-overlapping substring matches; lexicon must be sorted longest-first."""
    if not lexicon:
        return set()
    t = text.lower()
    n = len(t)
    covered = [False] * n
    found: set[str] = set()
    for phrase in lexicon:
        pl = phrase.lower()
        plen = len(pl)
        if plen == 0:
            continue
        start = 0
        while True:
            idx = t.find(pl, start)
            if idx == -1:
                break
            before_ok = idx == 0 or not t[idx - 1].isalnum()
            after_ok = idx + plen == n or not t[idx + plen].isalnum()
            if pl[0].isalnum() and (not before_ok or not after_ok):
                start = idx + 1
                continue
            if not any(covered[idx : idx + plen]):
                for j in range(idx, idx + plen):
                    covered[j] = True
                found.add(phrase)
            start = idx + 1
    return found


def _extract_full_text(pdf_path: Path) -> str:
    docs = PyPDFLoader(str(pdf_path)).load()
    parts: list[str] = []
    for d in docs:
        if d.page_content:
            parts.append(d.page_content)
    return "\n\n".join(parts)


class CategoryCount(BaseModel):
    id: str
    label: str
    count: int


class SkillCount(BaseModel):
    skill: str
    count: int


class ResumeAnalyticsResponse(BaseModel):
    """Aggregates from PDF text on disk. Not derived from embeddings or vector coordinates."""

    files_scanned: int
    categories: list[CategoryCount]
    skills: list[SkillCount]
    warnings: list[str] = Field(default_factory=list)
    skill_match_mode: str = Field(
        default="per_file_dedupe",
        description="Each skill counts at most once per PDF; totals are across files.",
    )


def compute_resume_analytics(
    *,
    uploads_dir: str | None = None,
    top_skills: int = 15,
    include_other: bool = True,
) -> ResumeAnalyticsResponse:
    root = Path(uploads_dir or settings.uploads_dir).resolve()
    warnings: list[str] = []
    if not root.is_dir():
        return ResumeAnalyticsResponse(
            files_scanned=0,
            categories=[],
            skills=[],
            warnings=[f"Upload directory does not exist: {root}"],
        )

    pdfs = sorted(root.glob("*.pdf"))
    if not pdfs:
        return ResumeAnalyticsResponse(files_scanned=0, categories=[], skills=[])

    total_cat: dict[str, int] = defaultdict(int)
    skill_totals: dict[str, int] = defaultdict(int)
    lexicon = _load_skills_lexicon()
    if not lexicon:
        warnings.append("Skills lexicon is empty or missing; skill chart will be empty.")

    scanned = 0
    for pdf_path in pdfs:
        try:
            text = _extract_full_text(pdf_path)
        except Exception as e:
            warnings.append(f"{pdf_path.name}: failed to read ({e!s})")
            continue
        scanned += 1
        for cat, n in _section_char_counts(text).items():
            total_cat[cat] += n
        for skill in _find_skills_in_text(text, lexicon):
            skill_totals[skill] += 1

    categories_out: list[CategoryCount] = []
    for cid, label in _CATEGORY_LABELS.items():
        if cid == "other" and not include_other:
            continue
        n = int(total_cat.get(cid, 0))
        if n > 0:
            categories_out.append(CategoryCount(id=cid, label=label, count=n))

    # Stable order: by count desc, then label
    categories_out.sort(key=lambda c: (-c.count, c.label))

    skills_sorted = sorted(skill_totals.items(), key=lambda x: (-x[1], x[0].lower()))[: max(0, top_skills)]
    skills_out = [SkillCount(skill=s, count=c) for s, c in skills_sorted]

    return ResumeAnalyticsResponse(
        files_scanned=scanned,
        categories=categories_out,
        skills=skills_out,
        warnings=warnings,
    )
