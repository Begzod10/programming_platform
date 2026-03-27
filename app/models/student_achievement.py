from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import Student
    from app.models.achievement import Achievement


class StudentAchievement(Base):
    __tablename__ = "student_achievements"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign keys
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )
    achievement_id: Mapped[int] = mapped_column(
        ForeignKey("achievements.id", ondelete="CASCADE"),
        nullable=False
    )

    # Timestamp
    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="student_achievements"
    )
    achievement: Mapped["Achievement"] = relationship(
        "Achievement",
        back_populates="student_achievements"
    )

    def __repr__(self) -> str:
        return f"<StudentAchievement(student_id={self.student_id}, achievement_id={self.achievement_id})>"