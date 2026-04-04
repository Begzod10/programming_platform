from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from typing import List


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    badge_image_url: Mapped[str] = mapped_column(String(255))
    points_reward: Mapped[int] = mapped_column(Integer)
    criteria_type: Mapped[str] = mapped_column(String(50))
    criteria_value: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student_achievements: Mapped[List["StudentAchievement"]] = relationship(
        "StudentAchievement",
        back_populates="achievement",
        cascade="all, delete-orphan",
        passive_deletes=True
    )