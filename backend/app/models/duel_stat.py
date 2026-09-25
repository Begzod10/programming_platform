"""Win/games counters for the 1-vs-1 duel leaderboard (logged-in students only)."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class DuelStat(Base):
    __tablename__ = "duel_stats"

    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True,
    )
    wins: Mapped[int] = mapped_column(Integer, default=0, nullable=False, server_default="0")
    games: Mapped[int] = mapped_column(Integer, default=0, nullable=False, server_default="0")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),
    )
