"""Detects a project submission that is just the lesson's own sample
project ("namuna"), copied.

Every lesson can carry a LessonSample — the fully-working reference
implementation shown to the student on the lesson page (see
lesson_sample.py / the /lessons/{id}/sample endpoint). It necessarily
satisfies the lesson's own requirements/technologies perfectly, so the AI
grader in grok_review.py — which only checks "does this code fulfil the
task" — has no way to tell a genuine solution from the sample pasted back
verbatim. This module gives ai_review_service a deterministic, un-gameable
signal for that specific case, independent of anything the AI decides.

Deliberately NOT a general plagiarism/similarity detector (no fuzzy match
against other students' submissions, no web search) — narrowly scoped to
"is this suspiciously close to the ONE reference solution we ourselves
handed the student", which is cheap, exact, and has no false-positive risk
from unrelated students converging on similar code.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson_sample import LessonSample

# Ratio (SequenceMatcher, 0-1) above which a submission is treated as "this
# is the sample, not the student's own work". Picked high — this must only
# fire on a near-verbatim paste (identical structure/logic, at most
# renamed variables or reformatted whitespace), never on two independently
# written solutions that happen to converge on a similar approach.
COPY_RATIO_THRESHOLD = 0.90

# Below this many normalized characters, similarity is meaningless — a
# one-line "<h1>Salom</h1>" lesson has exactly one reasonable answer, and
# every genuine student submission would score just as "similar" as an
# actual copy. Only compare once there's enough code for structural
# similarity to actually mean something.
MIN_COMPARISON_LENGTH = 200


@dataclass(frozen=True)
class SampleCopyResult:
    available: bool  # False = nothing to compare (no sample, or too short)
    ratio: float = 0.0
    is_copy: bool = False


_NOISE_LINE = re.compile(r"^(#{2,3}\s|```)")


def _normalize(text: str) -> str:
    """Collapse formatting noise so only structure/logic drives the
    similarity score, not indentation, blank lines, or (for repo snapshots)
    the "### path" / fenced-code-block markup github_repo_service wraps
    each file in."""
    if not text:
        return ""
    lines = (
        line.strip()
        for line in text.splitlines()
        if line.strip() and not _NOISE_LINE.match(line.strip())
    )
    return re.sub(r"\s+", " ", " ".join(lines)).strip()


def _sample_code_text(sample: LessonSample) -> str:
    """Flatten whichever code fields this sample actually uses (html/css/js
    for sample_type="web", or code_files_json's {filename, language, code}
    entries for sample_type="code"/"python"/"sql") into one blob."""
    parts = [p for p in (sample.html_code, sample.css_code, sample.js_code) if p]
    if sample.code_files_json:
        try:
            files = json.loads(sample.code_files_json)
        except (TypeError, ValueError):
            files = []
        if isinstance(files, list):
            parts.extend(
                f["code"] for f in files
                if isinstance(f, dict) and f.get("code")
            )
    return "\n".join(parts)


async def load_lesson_sample_code(db: AsyncSession, lesson_id: Optional[int]) -> Optional[str]:
    """The lesson's sample code as one flattened blob, or None if the
    lesson has no LessonSample (most lessons don't) or it carries no code."""
    if lesson_id is None:
        return None
    sample = (await db.execute(
        select(LessonSample).where(LessonSample.lesson_id == lesson_id)
    )).scalar_one_or_none()
    if sample is None:
        return None
    code = _sample_code_text(sample)
    return code or None


def check_against_sample(submission_text: str, sample_text: Optional[str]) -> SampleCopyResult:
    """Compare a submission's repo-snapshot text (see
    github_repo_service.fetch_*_snapshot's content_text) against the
    lesson's sample code. Pure function — no I/O — so it's trivial to unit
    test against fixed strings.
    """
    if not sample_text or not submission_text:
        return SampleCopyResult(available=False)

    norm_submission = _normalize(submission_text)
    norm_sample = _normalize(sample_text)
    if len(norm_sample) < MIN_COMPARISON_LENGTH or len(norm_submission) < MIN_COMPARISON_LENGTH:
        return SampleCopyResult(available=False)

    ratio = SequenceMatcher(None, norm_submission, norm_sample).ratio()
    return SampleCopyResult(
        available=True,
        ratio=ratio,
        is_copy=ratio >= COPY_RATIO_THRESHOLD,
    )
