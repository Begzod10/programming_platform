from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, UniqueConstraint
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
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    github_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    live_demo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    project_files: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    technologies_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty_level: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Draft")
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    instructor_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_improvements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_bugs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)

    # Anti-cheat metrics recorded at submission time
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    keystroke_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    paste_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    code_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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


class ProjectLike(Base):
    """One row per (student, project) like — the real per-student dedup
    mechanism for `Project.likes_count`.

    Before this table existed, `likes_count` was a bare counter bumped on
    every POST /like with no identity check at all (only self-likes were
    blocked) — the same other student could like a project unlimited
    times. The unique constraint below is what makes a repeat like a
    clean no-op instead of counter spam; see
    `ProjectService.like_project`/`unlike_project`, which recompute
    `likes_count` from this table rather than incrementing it in place.
    """
    __tablename__ = "project_likes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (
        UniqueConstraint("student_id", "project_id", name="uq_project_like_student_project"),
    )