"""Notification emission helpers.

Every public helper is best-effort: it writes one notification row inside a
SAVEPOINT and commits it, and NEVER raises into the caller. Notifications are
purely additive — if writing one fails, the originating action (project review,
achievement award, …) must still succeed. Callers invoke these right after the
event they describe has itself been committed.
"""
import logging
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification

logger = logging.getLogger(__name__)


async def _unread_count(db: AsyncSession, student_id: int) -> int:
    return (await db.execute(
        select(func.count(Notification.id)).where(
            Notification.student_id == student_id,
            Notification.is_read == False,  # noqa: E712
        )
    )).scalar() or 0


async def _broadcast_new(db: AsyncSession, student_id: int, note: Notification) -> None:
    """Push a freshly-emitted notification to the student's live socket(s).

    Best-effort: a failed push must never undo the already-committed row, so it
    swallows everything. Safe to call after commit — the session uses
    expire_on_commit=False, so ``note``'s attributes stay loaded.
    """
    try:
        from app.schemas.notification import NotificationRead
        from app.ws.manager import notif_ws_manager
        await notif_ws_manager.broadcast(student_id, {
            "type": "notification",
            "notification": NotificationRead.model_validate(note).model_dump(mode="json"),
            "unread_count": await _unread_count(db, student_id),
        })
    except Exception as e:  # noqa: BLE001 — realtime push is purely additive
        logger.debug("notification ws push skipped (student=%s): %s", student_id, e)


async def broadcast_unread(db: AsyncSession, student_id: int) -> None:
    """Push just the current unread count so the header bell re-syncs instantly
    across the student's other open tabs/devices (used after read / read-all)."""
    try:
        from app.ws.manager import notif_ws_manager
        await notif_ws_manager.broadcast(student_id, {
            "type": "unread",
            "unread_count": await _unread_count(db, student_id),
        })
    except Exception as e:  # noqa: BLE001
        logger.debug("notification ws unread push skipped (student=%s): %s", student_id, e)


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
    except Exception as e:  # noqa: BLE001 — best-effort, must never propagate
        logger.warning("notification emit failed (student=%s type=%s): %s", student_id, type, e)
        try:
            await db.rollback()
        except Exception:
            pass
        return None

    # Committed. Push it to any live WebSocket the student has open — best-effort,
    # never affects the caller even if the socket layer errors.
    await _broadcast_new(db, student_id, note)
    return note


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


async def notify_games_unlocked(db: AsyncSession, student_id: int) -> Optional[Notification]:
    """Fired when a student meets the daily quota and the leisure sections
    unlock — rendered as the celebratory "Games Unlocked 🎮" toast."""
    return await _emit(
        db, student_id, type="games_unlocked", tone="star", title="",
        icon="🎮", link="/student/duel",
    )
