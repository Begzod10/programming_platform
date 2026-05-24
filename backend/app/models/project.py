from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


def utcnow():
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    github_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    live_demo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    project_files: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    technologies_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty_level: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Draft")
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    instructor_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)

    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="projects",
        passive_deletes=True
    )
    lessons: Mapped[List["Lesson"]] = relationship(
        "Lesson",
        back_populates="project"
    )