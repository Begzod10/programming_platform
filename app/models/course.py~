from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Text, func, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import Student
    from app.models.lesson import Lesson

# ✅ Junction table - student_courses
student_courses = Table(
    "student_courses",
    Base.metadata,
    Column("student_id", ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True
)


class Course(Base):
    __tablename__ = "courses"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Basic info
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Foreign key
    instructor_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )

    # Course details
    difficulty_level: Mapped[str] = mapped_column(String(20), nullable=False)
    duration_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    max_points: Mapped[int] = mapped_column(Integer, nullable=False)

    # Media URLs (ikkalasi ham - compatibility uchun)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    video_intro_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    syllabus_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    # Timestamps
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
    instructor: Mapped["Student"] = relationship(
        "Student",
        foreign_keys=[instructor_id],
        backref="taught_courses"
    )

    students: Mapped[List["Student"]] = relationship(
        "Student",
        secondary=student_courses,
        back_populates="enrolled_courses"
    )

    lessons: Mapped[List["Lesson"]] = relationship(
        "Lesson",
        back_populates="course",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Course(id={self.id}, title={self.title}, instructor_id={self.instructor_id})>"
