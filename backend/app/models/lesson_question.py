from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


def utcnow():
    return datetime.now(timezone.utc)


class LessonQuestion(Base):
    """Standard question bank attached to a lesson. Reusable across game sessions."""
    __tablename__ = "lesson_questions"

    id:             Mapped[int]            = mapped_column(primary_key=True, autoincrement=True)
    lesson_id:      Mapped[int]            = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    question_text:  Mapped[str]            = mapped_column(Text, nullable=False)
    options:        Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # list of 2-4 strings (quiz kind only)
    correct_option: Mapped[Optional[int]]  = mapped_column(Integer, nullable=True)  # 0-indexed (quiz kind only)
    time_limit:     Mapped[int]            = mapped_column(Integer, default=30, nullable=False)
    points:         Mapped[int]            = mapped_column(Integer, default=1000, nullable=False)
    order_index:    Mapped[int]            = mapped_column(Integer, default=0, nullable=False)
    created_at:     Mapped[datetime]       = mapped_column(DateTime(timezone=True), default=utcnow)

    # ── Bug-hunt kind ──────────────────────────────────────────────────
    # Mirrors GameQuestion's discriminator (see team_game.py). Here the bank
    # keeps bug_line/distractor_lines as separate fields rather than a
    # pre-shuffled options list, since import_questions_from_lesson reshuffles
    # them fresh into a GameQuestion on every import (same helper the
    # single-question add_bug_question endpoint uses).
    question_kind:     Mapped[str]            = mapped_column(String(20), default="quiz", nullable=False)
    code_snippet:       Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code_language:      Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bug_line:            Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-indexed
    distractor_lines:    Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # 1-indexed line numbers
    bug_explanation:     Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bug_explanation_ru:  Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    lesson: Mapped["Lesson"] = relationship("Lesson", foreign_keys=[lesson_id])
