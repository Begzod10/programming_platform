from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, Text, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.lesson import Lesson
    from app.models.user import Student


class LessonFeedback(Base):
    """Per-student per-lesson rating + optional comment.

    Used by teachers and admins to spot lessons that students find
    confusing, too easy, or missing context. Students can update their
    own feedback at any time — only one row per (student, lesson).
    """
    __tablename__ = "lesson_feedback"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    student: Mapped["Student"] = relationship("Student")
    lesson: Mapped["Lesson"] = relationship("Lesson")

    __table_args__ = (
        UniqueConstraint("student_id", "lesson_id", name="uq_lesson_feedback_student_lesson"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_lesson_feedback_rating_range"),
    )

    def __repr__(self) -> str:
        return (
            f"<LessonFeedback(id={self.id}, lesson_id={self.lesson_id}, "
            f"student_id={self.student_id}, rating={self.rating})>"
        )
