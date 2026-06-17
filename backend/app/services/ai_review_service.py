"""Core AI-review pipeline.

Two callers:
  1) POST /v1/ai/{project_id}/ai-review            — manual student trigger
  2) POST /v1/project/{project_id}/submit          — auto-trigger on submit

Both share this service so behavior stays in lockstep. The only knob is
`raise_on_error`: the manual endpoint raises HTTPException for any 4xx/5xx
condition so the student sees a clean error; the auto-trigger swallows
errors and returns {'success': False, 'reason': ...} so a flaky AI
provider never blocks lesson submission.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.project import Project
from app.services.github_repo_service import (
    fetch_github_snapshot,
    fetch_zip_snapshot,
    parse_github_url,
)
from app.services.grok_service import analyze_project_with_grok
from app.services.lesson_context_resolver import load_lesson_context_for_project
from app.services.ranking_service import RankingService

logger = logging.getLogger(__name__)


def _utc_day_start() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


async def count_reviews_today(db: AsyncSession, student_id: int) -> int:
    """How many AI reviews this student has consumed in the current UTC day.

    Counts any project with reviewed_at within today. Manual + auto-trigger
    share the same quota; the auto-trigger is naturally bounded by the
    per-lesson unique submission constraint, so this mostly caps abuse via
    the manual button.
    """
    start = _utc_day_start()
    end = start + timedelta(days=1)
    result = await db.execute(
        select(func.count(Project.id)).where(
            Project.student_id == student_id,
            Project.reviewed_at >= start,
            Project.reviewed_at < end,
        )
    )
    return int(result.scalar() or 0)


class _SkipReview(Exception):
    """Internal: AI review can't run — surfaced as 400/429/502 or swallowed."""
    def __init__(self, http_status: int, detail: str):
        self.http_status = http_status
        self.detail = detail
        super().__init__(detail)


async def run_ai_review_for_project(
        db: AsyncSession,
        project: Project,
        *,
        raise_on_error: bool = True,
) -> dict:
    """Run the full pipeline for one project.

    Args:
        db: active async session — caller manages the outer transaction.
            This function commits its own writes.
        project: the Project row to review. Must already exist with at
            least one of github_url / project_files set, otherwise the
            review is skipped.
        raise_on_error: If True (manual button), raises HTTPException for
            any failure path so the endpoint returns the right status
            code. If False (auto-trigger), returns a dict with
            success=False so the caller can keep going.

    Returns:
        On success: {success: True, grade, points, feedback, strengths,
            improvements, summary, provider, source, files_reviewed,
            authorship, old_points, new_points, reviews_remaining_today}
        On skipped (only when raise_on_error=False):
            {success: False, reason: str, http_status: int}
    """
    if settings.MAX_AI_REVIEWS_PER_DAY <= 0:
        return _fail(raise_on_error, status.HTTP_503_SERVICE_UNAVAILABLE,
                     "AI baholash hozircha o'chirilgan")

    # Block re-review on reviewed_at (not just status="Approved"). Prevents
    # bypass via re-submission cycles that change status but leave the
    # original AI review timestamp in place.
    if project.reviewed_at is not None:
        return _fail(raise_on_error, 400,
                     "Bu loyiha allaqachon baholangan, qayta AI baholash mumkin emas")

    # Source dispatch: prefer GitHub URL (richer signal); fall back to ZIP.
    source: str
    if project.github_url:
        if parse_github_url(project.github_url) is None:
            return _fail(raise_on_error, 400,
                         "GitHub URL formati noto'g'ri "
                         "(faqat https://github.com/owner/repo)")
        source = "github"
    elif project.project_files:
        source = "zip"
    else:
        return _fail(raise_on_error, 400,
                     "AI baholash uchun GitHub URL yoki ZIP fayl kerak")

    # Daily cap is a backstop against abuse — covers both manual triggers
    # and auto-triggers. With the per-project block above and per-lesson
    # unique submission constraint elsewhere, abuse paths are narrow.
    used_today = await count_reviews_today(db, project.student_id)
    if used_today >= settings.MAX_AI_REVIEWS_PER_DAY:
        return _fail(raise_on_error, status.HTTP_429_TOO_MANY_REQUESTS,
                     f"Bugun AI baholash limiti tugadi "
                     f"({settings.MAX_AI_REVIEWS_PER_DAY}/kun). "
                     f"Ertaga qayta urinib ko'ring.")

    # Real code, not just metadata. If snapshot can't be built, refuse the
    # AI call entirely — no point spending tokens to hallucinate.
    if source == "github":
        snapshot = await fetch_github_snapshot(project.github_url)
        source_label = "GitHub repo"
    else:
        snapshot = fetch_zip_snapshot(project.project_files)
        source_label = "ZIP fayl"

    if not snapshot["exists"]:
        return _fail(raise_on_error, 400,
                     f"{source_label} o'qib bo'lmadi: "
                     f"{snapshot.get('error') or 'nomalum xato'}")
    if not snapshot["content_text"]:
        return _fail(raise_on_error, 400,
                     f"{source_label} bo'sh yoki o'qiladigan fayllar topilmadi")

    repo_summary = (
        f"manba={source_label}, "
        f"default_branch={snapshot['default_branch']}, "
        f"jami fayl soni={snapshot['file_count']}, "
        f"kiritildi ({len(snapshot['files_included'])}): "
        f"{', '.join(snapshot['files_included'])}"
        + (" [truncated]" if snapshot["truncated"] else "")
    )

    technologies = (project.technologies_used.split(",")
                    if project.technologies_used else [])

    # Lesson + course context — without this the AI grader uses a generic
    # persona and HTML/CSS submissions get reviewed against an invented
    # Python/Flask-style rubric. Returns None for standalone projects
    # (no Submission row); the AI then falls back to "dasturlash o'qituvchisi".
    lesson_context = await load_lesson_context_for_project(
        db, project_id=project.id
    )

    review = await analyze_project_with_grok(
        title=project.title,
        description=project.description or "",
        github_url=project.github_url or f"(ZIP: {project.project_files})",
        technologies=technologies,
        difficulty_level=str(project.difficulty_level or "Easy"),
        repo_content=snapshot["content_text"],
        repo_summary=repo_summary,
        authorship=snapshot.get("authorship"),
        lesson_context=lesson_context,
    )

    # AI call failed (all providers down, no key set anywhere, etc.).
    # No DB writes, no quota consumed.
    if review.get("error"):
        return _fail(raise_on_error, status.HTTP_502_BAD_GATEWAY,
                     review.get("feedback") or "AI baholash muvaffaqiyatsiz")

    # Default to 0 (NOT 60) — malformed AI response must never grant free points.
    new_points = int(review.get("points", 0) or 0)
    new_points = max(0, min(100, new_points))

    old_points = project.points_earned or 0
    ranking_service = RankingService(db)
    if old_points > 0:
        await ranking_service.subtract_points_from_student(
            project.student_id, old_points)
    if new_points > 0:
        await ranking_service.add_points_to_student(
            project.student_id, new_points)

    project.instructor_feedback = review.get("feedback", "")
    project.grade = review.get("grade", "F")
    project.points_earned = new_points
    project.status = "Approved" if new_points >= 75 else "Rejected"
    project.reviewed_at = datetime.now(timezone.utc)

    await db.commit()

    authorship = snapshot.get("authorship") or {}
    return {
        "success": True,
        "project_id": project.id,
        "source": source,
        "old_points": old_points,
        "new_points": new_points,
        "reviews_remaining_today": max(
            0, settings.MAX_AI_REVIEWS_PER_DAY - used_today - 1
        ),
        "files_reviewed": snapshot["files_included"],
        "authorship": {
            "available": authorship.get("available", False),
            "is_fork": authorship.get("is_fork", False),
            "parent_repo": authorship.get("parent_repo"),
            "commit_count": authorship.get("commit_count"),
            "unique_authors": authorship.get("unique_authors"),
            "owner_is_contributor": authorship.get("owner_is_contributor"),
        },
        **{k: v for k, v in review.items() if k != "error"},
    }


def _fail(raise_on_error: bool, http_status: int, detail: str) -> dict:
    """Either raise an HTTPException or return a 'skipped' dict."""
    if raise_on_error:
        raise HTTPException(status_code=http_status, detail=detail)
    logger.info("[ai-auto] skipped (HTTP %d): %s", http_status, detail)
    return {"success": False, "reason": detail, "http_status": http_status}
