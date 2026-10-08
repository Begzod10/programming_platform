"""Daily learning-quota, games-lock, penalties and quota-streak models.

The platform requires students to complete a daily lesson quota before the
leisure sections (early-learning, 1-vs-1 duel) unlock. Uncompleted lessons
carry over to the next day's mandatory workload (uncapped) and accrue a points
penalty at end-of-day. A separate *quota* streak (distinct from the activity
streak on Student) grants a small nightly yield.

State lives in one hot per-day row (StudentDailyProgress); everything else is
append-only audit (PenaltyLog, StreakBonusLog) plus a single live-streak row
(StreakTracker). "completed today" is always reconciled from
lesson_completions.completed_at, so the cached counter here can never drift
permanently.
"""
from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    Integer, Boolean, Date, DateTime, String, ForeignKey, UniqueConstraint,
    Index, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class StudentDailyProgress(Base):
    """One row per (student, Tashkent-calendar day). Source of truth for the
    lock state and the day's quota math."""
    __tablename__ = "student_daily_progress"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    quota_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # required = base_required + carried_in  (denormalized for cheap reads)
    base_required: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    carried_in: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    required: Mapped[int] = mapped_column(Integer, nullable=False, default=2)

    # cached count of lessons completed on this day; EOD recomputes from
    # lesson_completions so a missed increment self-heals.
    completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    unlocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    unlocked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # written by the end-of-day job
    processed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    penalty_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    carried_out: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("student_id", "quota_date", name="uq_daily_progress_student_date"),
        Index("ix_daily_progress_date_processed", "quota_date", "processed"),
    )


class PenaltyLog(Base):
    """Append-only record of each end-of-day points penalty (audit / disputes /
    UI history). Immutable even if a day is later recomputed."""
    __tablename__ = "quota_penalty_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    quota_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    lessons_missed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    points_deducted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # actually removed (post 0-floor)
    points_before: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    points_after: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reason: Mapped[str] = mapped_column(String(40), nullable=False, default="daily_quota_miss")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class StreakTracker(Base):
    """The student's single live *quota* streak (consecutive days the base quota
    was met) and the earnings baseline for the nightly yield."""
    __tablename__ = "quota_streak_tracker"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False, unique=True)

    started_on: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    length: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    best_length: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_qualified_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # lifetime_points snapshot at streak start; bonus_awarded_total is excluded
    # from the yield base so the bonus never compounds into itself.
    base_points_snapshot: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bonus_awarded_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class StreakBonusLog(Base):
    """Append-only record of each nightly streak yield (for the dashboard)."""
    __tablename__ = "quota_streak_bonus_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    quota_date: Mapped[date] = mapped_column(Date, nullable=False)

    streak_length: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    base_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # earnings in streak
    bonus_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
