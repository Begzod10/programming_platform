from datetime import datetime
from typing import Literal, TYPE_CHECKING
from sqlalchemy import Integer, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import Student


class Ranking(Base):
    __tablename__ = "rankings"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign key
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    # ✅ BALLAR TIZIMI (kunlik → haftalik → oylik → jami)
    daily_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Bugungi ball
    weekly_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Haftalik ball
    monthly_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Oylik ball
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Jami ball

    # Reytinglar
    global_rank: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Umumiy reyting
    level_rank: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Level ichida reyting

    # Statistika
    projects_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_grade: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Vaqtlar
    last_calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    last_daily_reset: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    last_weekly_reset: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    last_monthly_reset: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationship
    student: Mapped["Student"] = relationship("Student", back_populates="ranking")

    # ✅ Helper method
    def get_points_for_period(self, period: Literal["daily", "weekly", "monthly", "all"]) -> int:
        """Period bo'yicha pointsni qaytarish"""
        period_map = {
            "daily": self.daily_points,
            "weekly": self.weekly_points,
            "monthly": self.monthly_points,
            "all": self.total_points
        }
        return period_map.get(period, self.total_points)

    def __repr__(self) -> str:
        return f"<Ranking(student_id={self.student_id}, total_points={self.total_points}, global_rank={self.global_rank})>"