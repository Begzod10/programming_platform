"""Daily learning-quota / games-lock engine.

One module owns the rule so the API, the gating dependency, the lesson-completion
hook and the nightly job all agree. "Today" is the Asia/Tashkent calendar day
(single-tz platform). Everything is derived from lesson_completions.completed_at,
so the cached counters self-heal.

Public surface:
  get_today(db, student_id)            -> QuotaStatus      (read, used by API + dependency)
  on_lesson_completed(db, student, id) -> QuotaStatus      (hook from lesson_service)
  seed_next_day(db, student_id, day, carried_in)           (EOD)
  process_eod_for_student(db, rs, student, day)            (EOD, one student)
"""
import logging
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import Student
from app.models.lesson import Lesson, LessonCompletion
from app.models.course import student_courses
from app.models.daily_quota import (
    StudentDailyProgress, PenaltyLog, StreakTracker, StreakBonusLog,
)

logger = logging.getLogger(__name__)

TZ = ZoneInfo(settings.QUOTA_TZ)
BASE = settings.DAILY_QUOTA_LESSONS
PENALTY = settings.QUOTA_PENALTY_PER_LESSON
YIELD_RATE = settings.STREAK_YIELD_RATE


def today_local() -> date:
    return datetime.now(TZ).date()


def _day_bounds(day: date) -> tuple[datetime, datetime]:
    start = datetime(day.year, day.month, day.day, tzinfo=TZ)
    return start, start + timedelta(days=1)


@dataclass
class QuotaStatus:
    quota_date: date
    base_required: int
    carried_in: int
    required: int
    completed: int
    remaining: int
    unlocked: bool

    def as_dict(self) -> dict:
        return {
            "quota_date": self.quota_date.isoformat(),
            "base_required": self.base_required,
            "carried_in": self.carried_in,
            "required": self.required,
            "completed": self.completed,
            "remaining": self.remaining,
            "unlocked": self.unlocked,
            "unlock_mode": settings.QUOTA_UNLOCK_MODE,
        }


# ── helpers ─────────────────────────────────────────────────────────────────
def _unlock_threshold(required: int, base_required: int) -> int:
    """How many lessons unlock the games today. 'base' → the flat quota (your
    original "2 lessons"); 'full' → clear the whole backlog (2 + debt)."""
    return required if settings.QUOTA_UNLOCK_MODE == "full" else base_required


def _effective_required(required: int) -> int:
    cap = settings.QUOTA_DEBT_CAP
    if cap and cap > 0:
        return min(required, BASE + cap)
    return required


async def count_completed_on(db: AsyncSession, student_id: int, day: date) -> int:
    start, end = _day_bounds(day)
    return (await db.execute(
        select(func.count(LessonCompletion.id)).where(
            LessonCompletion.student_id == student_id,
            LessonCompletion.completed_at >= start,
            LessonCompletion.completed_at < end,
        )
    )).scalar() or 0


async def uncompleted_available(db: AsyncSession, student_id: int) -> int:
    """Lessons in the student's enrolled courses they haven't completed yet.
    Used so a student is never required/penalized for lessons that don't exist."""
    enrolled = select(student_courses.c.course_id).where(
        student_courses.c.student_id == student_id)
    total = (await db.execute(
        select(func.count(Lesson.id)).where(Lesson.course_id.in_(enrolled))
    )).scalar() or 0
    done = (await db.execute(
        select(func.count(LessonCompletion.id)).where(
            LessonCompletion.student_id == student_id)
    )).scalar() or 0
    return max(0, total - done)


async def _prev_carried_out(db: AsyncSession, student_id: int, day: date) -> int:
    prev = (await db.execute(
        select(StudentDailyProgress).where(
            StudentDailyProgress.student_id == student_id,
            StudentDailyProgress.quota_date == day - timedelta(days=1),
        )
    )).scalar_one_or_none()
    return prev.carried_out if prev else 0


async def _get_or_create(db: AsyncSession, student_id: int, day: date) -> StudentDailyProgress:
    row = (await db.execute(
        select(StudentDailyProgress).where(
            StudentDailyProgress.student_id == student_id,
            StudentDailyProgress.quota_date == day,
        )
    )).scalar_one_or_none()
    if row:
        return row
    carried_in = await _prev_carried_out(db, student_id, day)
    required = _effective_required(BASE + carried_in)
    row = StudentDailyProgress(
        student_id=student_id, quota_date=day,
        base_required=BASE, carried_in=carried_in, required=required,
    )
    db.add(row)
    await db.flush()
    return row


def _to_status(row: StudentDailyProgress, completed: int) -> QuotaStatus:
    threshold = _unlock_threshold(row.required, row.base_required)
    return QuotaStatus(
        quota_date=row.quota_date,
        base_required=row.base_required,
        carried_in=row.carried_in,
        required=row.required,
        completed=completed,
        remaining=max(0, threshold - completed),
        unlocked=completed >= threshold,
    )


# ── read (API + dependency) ──────────────────────────────────────────────────
async def get_today(db: AsyncSession, student_id: int) -> QuotaStatus:
    day = today_local()
    row = await _get_or_create(db, student_id, day)
    completed = await count_completed_on(db, student_id, day)
    status = _to_status(row, completed)
    # keep the cached mirror honest (cheap, self-healing)
    changed = False
    if row.completed != completed:
        row.completed, changed = completed, True
    if status.unlocked and not row.unlocked:
        row.unlocked, row.unlocked_at, changed = True, datetime.now(TZ), True
    if changed:
        await db.commit()
    return status


# ── completion hook (real-time unlock) ───────────────────────────────────────
async def on_lesson_completed(db: AsyncSession, student_id: int, lesson_id: int) -> QuotaStatus:
    """Call right after a LessonCompletion is committed. Recomputes today's
    count, flips the lock the instant the quota is met, and pushes the state +
    a 'games unlocked' notification over the WebSocket. Best-effort: never
    raises into the completion flow."""
    try:
        student = (await db.execute(
            select(Student).where(Student.id == student_id)
        )).scalar_one_or_none()
        if not student or student.is_demo:
            return None
        day = today_local()
        row = await _get_or_create(db, student_id, day)
        completed = await count_completed_on(db, student_id, day)
        status = _to_status(row, completed)
        just_unlocked = status.unlocked and not row.unlocked
        row.completed = completed
        if just_unlocked:
            row.unlocked, row.unlocked_at = True, datetime.now(TZ)
        await db.commit()
        if just_unlocked:
            await _emit_unlocked(db, student_id)
        await _push_quota(student_id, status)
        return status
    except Exception as e:  # noqa: BLE001 — quota tracking must not break lessons
        logger.warning("daily-quota hook failed (student=%s): %s", student_id, e)
        try:
            await db.rollback()
        except Exception:
            pass
        return None


# ── end-of-day (nightly job, one student) ────────────────────────────────────
async def process_eod_for_student(db: AsyncSession, ranking_service, student: Student, day: date) -> None:
    """Idempotent. Penalize missed lessons, carry the debt forward, update the
    streak + yield, and seed tomorrow. Skips demo/inactive students."""
    if student.is_demo or not student.is_active:
        return
    row = await _get_or_create(db, student.id, day)
    if row.processed:
        return

    completed = await count_completed_on(db, student.id, day)
    available = await uncompleted_available(db, student.id)
    # never demand more than (already done + lessons that actually exist)
    effective_required = min(row.required, completed + available)
    missed = max(0, effective_required - completed)

    row.completed = completed
    row.penalty_points = missed * PENALTY
    row.carried_out = missed
    row.processed = True
    if completed >= _unlock_threshold(row.required, row.base_required):
        row.unlocked = True

    # 1) penalty — floored at 0 by revoke_earned_points (no negative balances)
    if missed > 0:
        before = student.lifetime_points
        await ranking_service.revoke_earned_points(student.id, missed * PENALTY)
        await db.refresh(student)
        db.add(PenaltyLog(
            student_id=student.id, quota_date=day,
            lessons_missed=missed, points_deducted=min(missed * PENALTY, before),
            points_before=before, points_after=student.lifetime_points,
        ))

    # 2) streak — met the BASE quota today?
    if completed >= row.base_required:
        await _extend_streak(db, ranking_service, student, day)
    else:
        await _break_streak(db, student)

    # 3) seed tomorrow with the carried debt
    await seed_next_day(db, student.id, day + timedelta(days=1), carried_in=missed)
    await db.flush()


async def seed_next_day(db: AsyncSession, student_id: int, day: date, carried_in: int) -> None:
    row = await _get_or_create(db, student_id, day)
    row.carried_in = carried_in
    row.required = _effective_required(BASE + carried_in)
    row.base_required = BASE
    await db.flush()


async def _extend_streak(db, ranking_service, student: Student, day: date) -> None:
    st = (await db.execute(
        select(StreakTracker).where(StreakTracker.student_id == student.id)
    )).scalar_one_or_none()
    if not st:
        st = StreakTracker(student_id=student.id)
        db.add(st)
        await db.flush()

    if st.active and st.last_qualified_date == day - timedelta(days=1):
        st.length += 1
    else:  # (re)start the run — reset the earnings baseline
        st.started_on, st.length, st.active = day, 1, True
        st.base_points_snapshot = student.lifetime_points
        st.bonus_awarded_total = 0
    st.last_qualified_date = day
    st.best_length = max(st.best_length, st.length)

    earned = max(0, student.lifetime_points - st.base_points_snapshot - st.bonus_awarded_total)
    bonus = round(earned * YIELD_RATE)
    if bonus > 0:
        await ranking_service.credit_yield(student.id, bonus)
        st.bonus_awarded_total += bonus
        db.add(StreakBonusLog(
            student_id=student.id, quota_date=day,
            streak_length=st.length, base_points=earned, bonus_points=bonus,
        ))

    # mirror onto Student for the dashboard's existing streak widgets
    student.current_streak = st.length
    student.longest_streak = max(student.longest_streak or 0, st.length)


async def _break_streak(db, student: Student) -> None:
    st = (await db.execute(
        select(StreakTracker).where(StreakTracker.student_id == student.id)
    )).scalar_one_or_none()
    if st and st.active:
        st.active = False
        st.length = 0
    student.current_streak = 0


# ── websocket / notification side-effects (best-effort) ──────────────────────
async def _push_quota(student_id: int, status: QuotaStatus) -> None:
    try:
        from app.ws.manager import notif_ws_manager
        await notif_ws_manager.broadcast(student_id, {"type": "quota", **status.as_dict()})
    except Exception as e:  # noqa: BLE001
        logger.debug("quota ws push skipped (student=%s): %s", student_id, e)


async def _emit_unlocked(db: AsyncSession, student_id: int) -> None:
    try:
        from app.services import notification_service
        await notification_service.notify_games_unlocked(db, student_id)
    except Exception as e:  # noqa: BLE001
        logger.debug("games-unlocked notify skipped (student=%s): %s", student_id, e)
