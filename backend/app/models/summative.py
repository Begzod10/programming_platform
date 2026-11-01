"""A student's end-of-quarter "summative" test attempt.

The questions (with the correct answers and the shuffled option order) are
frozen into `questions` when the attempt starts and stay on the server: the
client only ever receives the text + options. Grading happens on submit.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class SummativeAttempt(Base):
    __tablename__ = "summative_attempts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    status: Mapped[str] = mapped_column(String(16), default="in_progress", server_default="in_progress")  # in_progress | finished
    finish_reason: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)  # submitted | time | violations
    scope: Mapped[str] = mapped_column(String(16), default="quarter", server_default="quarter")
    lang: Mapped[str] = mapped_column(String(4), default="uz", server_default="uz")
    total: Mapped[int] = mapped_column(Integer, default=0)
    correct: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[int] = mapped_column(Integer, default=0)  # percent
    time_limit_seconds: Mapped[int] = mapped_column(Integer, default=0)
    violations: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    # [{"text", "options": [...], "correct": int, "kind", "explanation"}]
    questions: Mapped[list] = mapped_column(JSON, nullable=False)
    answers: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # chosen option index or null, per question
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
