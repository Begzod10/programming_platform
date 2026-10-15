from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.utils.datetime_utils import utcnow


class ProjectCodeCheck(Base):
    """A short quiz on the student's OWN submitted code (see services/code_check_service.py).

    Created after a ZIP project was approved when it arrived faster than anyone could
    have written that much code (reason "pace"), or by random sampling ("random").
    It never changes points by itself: a failed / unanswered / unavailable check goes
    to the teacher's queue, and only the teacher can revoke the points.
    """
    __tablename__ = "project_code_checks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)

    reason: Mapped[str] = mapped_column(String(12), nullable=False)          # pace | random
    code_lines: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gap_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pace: Mapped[Optional[float]] = mapped_column(Float, nullable=True)        # lines per minute

    # pending -> passed | failed | suspicious | expired ; unavailable (no questions could be made) ; reviewed (teacher done)
    status: Mapped[str] = mapped_column(String(12), nullable=False, default="pending", index=True)
    questions_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)   # includes the answers: never sent to students
    answers_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    correct_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    blur_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # tab/window switches while answering
    times_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)       # per-question seconds, client-reported
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # server-measured

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # the code the questions are built from (kept: a GitHub repo can change or vanish, a ZIP can be deleted)
    code_excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # fast but passed the quiz: still shown to the teacher, below the cases that need them
    low_priority: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    needs_teacher: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    resolution: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)   # dismissed | points_revoked
    resolved_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    teacher_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
