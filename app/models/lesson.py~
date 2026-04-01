from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.project import Project


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

    # ✅ YANGI: Vazifa malumotlari
    task_title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # "Zadanie dlya studenta"
    task_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # "Opisanie zadaniya"
    task_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # "Trebovaniya" (list)
    task_technologies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # "Stek texnologiy" (comma-separated)
    task_deadline_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Muddati (kunlarda)

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

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    course: Mapped["Course"] = relationship("Course", back_populates="lessons")
    project: Mapped[Optional["Project"]] = relationship(
        "Project",
        back_populates="lessons"
    )