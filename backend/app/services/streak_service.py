"""Daily-activity streak tracker.

Lightweight by design — three integer columns on Student, one helper that
all activity endpoints call. We deliberately don't track per-day rows;
the current/longest-streak counters and the last_activity_date are enough
to drive the FE flame widget and Telegram "don't lose your streak" pings.

Day boundaries are evaluated against UTC. That's a deliberate simplification
— Uzbekistan is UTC+5 so a student finishing a lesson at 23:30 local
won't lose tomorrow's streak. If TZ-correctness ever matters, swap
`_today()` to use the student's profile TZ.
"""

from datetime import date, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Student


def _today() -> date:
    """Return the day the streak system considers 'now'. UTC for now."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).date()


async def bump_streak(db: AsyncSession, student_id: int) -> Optional[dict]:
    """Record activity for `student_id` against today.

    Idempotent within a day — many activity events in one day still count
    as one streak day. Returns the updated streak counters, or None if the
    student row doesn't exist (defensive — callers can ignore the result).

    Caller owns the session. We do NOT commit here; whichever endpoint
    triggered the activity is responsible for the transaction boundary,
    so the streak update lands atomically with the underlying work
    (or rolls back together).
    """
    res = await db.execute(select(Student).where(Student.id == student_id))
    student = res.scalar_one_or_none()
    if student is None:
        return None

    today = _today()
    last = student.last_activity_date

    if last == today:
        # Already counted today; no change.
        return _to_dict(student, today)

    if last is None or (today - last) > timedelta(days=1):
        # First-ever activity, or a gap of 2+ days — streak resets to 1.
        student.current_streak = 1
    else:
        # Exactly one day since last activity → continuation.
        student.current_streak = (student.current_streak or 0) + 1

    if (student.longest_streak or 0) < student.current_streak:
        student.longest_streak = student.current_streak

    student.last_activity_date = today
    await db.flush()

    return _to_dict(student, today)


def _to_dict(student: Student, today: date) -> dict:
    last = student.last_activity_date
    return {
        "current_streak": student.current_streak or 0,
        "longest_streak": student.longest_streak or 0,
        "last_activity_date": last.isoformat() if last else None,
        "today_active": last == today,
    }


async def get_streak(db: AsyncSession, student_id: int) -> dict:
    """Read-only streak summary for the /me/streak endpoint.

    Also lazily resets a stale current_streak to 0 if the student hasn't
    been active in 2+ days, so the widget doesn't keep showing a flame
    that should have died yesterday. The reset is in-memory only on read
    — bump_streak() will persist the next value when the student
    actually returns.
    """
    res = await db.execute(select(Student).where(Student.id == student_id))
    student = res.scalar_one_or_none()
    if student is None:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "last_activity_date": None,
            "today_active": False,
        }

    today = _today()
    last = student.last_activity_date
    effective_current = student.current_streak or 0
    if last is None or (today - last) > timedelta(days=1):
        effective_current = 0

    return {
        "current_streak": effective_current,
        "longest_streak": student.longest_streak or 0,
        "last_activity_date": last.isoformat() if last else None,
        "today_active": last == today,
    }
