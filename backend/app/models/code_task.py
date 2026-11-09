"""A coding task a teacher gives one student, and the student's submitted attempts.

Plain-string statuses (no DB enum) so adding a state never needs a migration.
See docs/superpowers/specs/2026-11-09-teacher-code-tasks-design.md.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.utils.datetime_utils import utcnow

ASSIGNED, SUBMITTED, RETURNED, GRADED = "assigned", "submitted", "returned", "graded"
CODE_TASK_LANGUAGES = ("html", "css", "javascript", "python", "sql", "json", "text")
MAX_CODE_CHARS = 100_000


class CodeTask(Base):
    __tablename__ = "code_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(16), nullable=False)
    starter_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    max_points: Mapped[int] = mapped_column(Integer, nullable=False, default=20, server_default="20")
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(12), nullable=False, default=ASSIGNED, server_default=ASSIGNED, index=True)
    draft_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    draft_saved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    graded_points: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    teacher_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    graded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # Language the AI summary is written in (the teacher's UI language when the task was created).
    review_lang: Mapped[str] = mapped_column(String(2), nullable=False, default="uz", server_default="uz")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class CodeTaskSubmission(Base):
    """One submitted attempt. The integrity numbers are client-reported hints for the teacher, never for the student."""
    __tablename__ = "code_task_submissions"
    __table_args__ = (UniqueConstraint("task_id", "attempt_no", name="uq_code_task_attempt"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("code_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt_no: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    active_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    typed_chars: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    pasted_chars: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    paste_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    ai_status: Mapped[str] = mapped_column(String(8), nullable=False, default="pending", server_default="pending")
    ai_review: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    return_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    returned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
