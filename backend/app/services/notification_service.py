"""Notification emission helpers.

Every public helper is best-effort: it writes one notification row inside a
SAVEPOINT and commits it, and NEVER raises into the caller. Notifications are
purely additive — if writing one fails, the originating action (project review,
achievement award, …) must still succeed. Callers invoke these right after the
event they describe has itself been committed.
"""
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification

logger = logging.getLogger(__name__)


async def _emit(
    db: AsyncSession,
    student_id: int,
    *,
    type: str,
    tone: str,
    title: str,
    body: Optional[str] = None,
    extra: Optional[str] = None,
    points: int = 0,
    link: Optional[str] = None,
    icon: Optional[str] = None,
) -> Optional[Notification]:
    if not student_id:
        return None
    note = Notification(
        student_id=student_id,
        type=type,
        tone=tone,
        title=(title or "")[:300],
        body=body,
        extra=(extra or None),
        points=points or 0,
        link=link,
        icon=icon,
    )
    try:
        # SAVEPOINT isolates a failed insert so it can't poison the caller's
        # session; the outer commit persists it.
        async with db.begin_nested():
            db.add(note)
            await db.flush()
        await db.commit()
        return note
    except Exception as e:  # noqa: BLE001 — best-effort, must never propagate
        logger.warning("notification emit failed (student=%s type=%s): %s", student_id, type, e)
        try:
            await db.rollback()
        except Exception:
            pass
        return None


async def notify_project_reviewed(db: AsyncSession, project) -> Optional[Notification]:
    """Emit a notification reflecting a project's current review status.

    Safe to call after any Approved/Rejected/Submitted transition — it no-ops
    for any other status.
    """
    status = (getattr(project, "status", "") or "").lower()
    title = getattr(project, "title", None) or "Loyiha"
    sid = getattr(project, "student_id", None)

    if status in ("approved", "reviewed"):
        return await _emit(
            db, sid, type="project_approved", tone="ok", title=title,
            extra=(getattr(project, "grade", None) or None),
            points=getattr(project, "points_earned", 0) or 0,
            link="/student/projects",
        )
    if status == "rejected":
        fb = getattr(project, "instructor_feedback", None)
        return await _emit(
            db, sid, type="project_rejected", tone="bad", title=title,
            body=(fb[:500] if fb else None),
            link="/student/projects",
        )
    if status in ("submitted", "under review"):
        return await _emit(
            db, sid, type="project_submitted", tone="wait", title=title,
            link="/student/projects",
        )
    return None


async def notify_achievement_earned(db: AsyncSession, student_id: int, achievement) -> Optional[Notification]:
    name = getattr(achievement, "name", None) or "Yutuq"
    return await _emit(
        db, student_id, type="achievement", tone="star", title=name,
        body=getattr(achievement, "description", None),
        points=getattr(achievement, "points_reward", 0) or 0,
        icon=getattr(achievement, "badge_image_url", None),
        link="/student/achievements",
    )


async def notify_certificate_earned(db: AsyncSession, student_id: int, course_title: str) -> Optional[Notification]:
    return await _emit(
        db, student_id, type="certificate", tone="cert", title=(course_title or "Kurs"),
        link="/student/degrees",
    )
