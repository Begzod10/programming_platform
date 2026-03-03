from datetime import datetime
from typing import List
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

# Junction table for student-course enrollment
student_courses = Table(
    "student_courses",
    Base.metadata,
    Column("student_id", ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True
)


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(String(500))
    instructor_id: Mapped[int] = mapped_column(Integer)  # assuming instructors table exists

    difficulty_level: Mapped[str] = mapped_column(String(20))
    duration_weeks: Mapped[int] = mapped_column(Integer)
    max_points: Mapped[int] = mapped_column(Integer)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    students: Mapped[List["Student"]] = relationship(
        "Student",
        secondary="student_courses",
        back_populates="enrolled_courses"
    )
