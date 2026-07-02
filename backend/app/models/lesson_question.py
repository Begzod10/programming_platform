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
    options:        Mapped[list]           = mapped_column(JSON, nullable=False)  # list of 2-4 strings
    correct_option: Mapped[int]            = mapped_column(Integer, nullable=False)  # 0-indexed
    time_limit:     Mapped[int]            = mapped_column(Integer, default=30, nullable=False)
    points:         Mapped[int]            = mapped_column(Integer, default=1000, nullable=False)
    order_index:    Mapped[int]            = mapped_column(Integer, default=0, nullable=False)
    created_at:     Mapped[datetime]       = mapped_column(DateTime(timezone=True), default=utcnow)

    lesson: Mapped["Lesson"] = relationship("Lesson", foreign_keys=[lesson_id])
