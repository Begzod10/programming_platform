from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class StudentAchievement(Base):
    __tablename__ = "student_achievements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    achievement_id: Mapped[int] = mapped_column(ForeignKey("achievements.id"), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement")
