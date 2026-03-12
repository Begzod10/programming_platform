from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    github_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    live_demo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    project_files: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    technologies_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    difficulty_level: Mapped[str] = mapped_column(String(20), nullable=False)

    status: Mapped[str] = mapped_column(String(20), default="Draft")  # Draft, Submitted, etc.
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    instructor_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)

    views_count: Mapped[int] = mapped_column(Integer, default=0)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)

    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student: Mapped["Student"] = relationship("Student", back_populates="projects")
