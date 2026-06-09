"""Course category — single-category-per-course classification.

Teachers create categories implicitly by typing a new name on the course form;
the backend auto-creates the row if it doesn't already exist (case-insensitive
match by name). Categories are global, shared across instructors.
"""
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import Student


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    created_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("students.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    courses: Mapped[List["Course"]] = relationship(
        "Course",
        back_populates="category",
        passive_deletes=True,
    )
    created_by: Mapped[Optional["Student"]] = relationship(
        "Student",
        foreign_keys=[created_by_id],
    )
