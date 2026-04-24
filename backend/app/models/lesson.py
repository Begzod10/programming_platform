from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.project import Project
    from app.models.user import Student


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)
    points_reward: Mapped[int] = mapped_column(Integer, default=10, server_default="10")

    # Vazifa ma'lumotlari
    task_title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    task_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    task_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    task_technologies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    task_deadline_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Kontent turlari
    text_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code_language: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    video_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Project relationship
    project_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="lessons")
    project: Mapped[Optional["Project"]] = relationship(
        "Project",
        back_populates="lessons"
    )

    from typing import List
    exercises: Mapped[List["Exercise"]] = relationship(
        "Exercise", back_populates="lesson", cascade="all, delete-orphan"
    )

    completions: Mapped[List["LessonCompletion"]] = relationship(
        "LessonCompletion",
        back_populates="lesson",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Lesson(id={self.id}, title={self.title}, course_id={self.course_id})>"


class LessonCompletion(Base):
    """Dars tugatilganligini kuzatish"""
    __tablename__ = "lesson_completions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="lesson_completions")
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="completions")

    # Unique constraint - student bir darsni faqat bir marta complete qilishi mumkin
    __table_args__ = (
        UniqueConstraint("student_id", "lesson_id", name="uq_student_lesson_completion"),
    )

    def __repr__(self) -> str:
        return f"<LessonCompletion(student_id={self.student_id}, lesson_id={self.lesson_id})>"

