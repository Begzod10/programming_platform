from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, ForeignKey, DateTime, Text, Index, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class Submission(Base):
    __tablename__ = "submissions"
    # Partial unique index: a student can only have one submission per lesson.
    # NULL lesson_id (standalone projects) is allowed to repeat. Applied on
    # fresh DBs via create_all; existing DBs need a manual migration.
    __table_args__ = (
        Index(
            "uq_submission_student_lesson",
            "student_id",
            "lesson_id",
            unique=True,
            postgresql_where=text("lesson_id IS NOT NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    lesson_id: Mapped[Optional[int]] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True)

    github_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    live_demo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Submitted")
    instructor_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    points_earned: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    student: Mapped["Student"] = relationship("Student")
    project: Mapped["Project"] = relationship("Project")
    lesson: Mapped[Optional["Lesson"]] = relationship("Lesson")