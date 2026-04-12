from datetime import datetime
from typing import Literal, TYPE_CHECKING
from sqlalchemy import Integer, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import Student


class Ranking(Base):
    __tablename__ = "rankings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    daily_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    weekly_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    monthly_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    global_rank: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    daily_rank: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    weekly_rank: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    monthly_rank: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level_rank: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    projects_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_grade: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    last_calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_daily_reset: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_weekly_reset: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_monthly_reset: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    student: Mapped["Student"] = relationship("Student", back_populates="ranking")

    def get_points_for_period(self, period: Literal["daily", "weekly", "monthly", "all"]) -> int:
        return {"daily": self.daily_points, "weekly": self.weekly_points,
                "monthly": self.monthly_points, "all": self.total_points}.get(period, self.total_points)

    def get_rank_for_period(self, period: Literal["daily", "weekly", "monthly", "all"]) -> int:
        return {"daily": self.daily_rank, "weekly": self.weekly_rank,
                "monthly": self.monthly_rank, "all": self.global_rank}.get(period, self.global_rank)

    def __repr__(self):
        return f"<Ranking(student_id={self.student_id}, total={self.total_points}, rank={self.global_rank})>"