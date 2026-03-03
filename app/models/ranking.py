from datetime import datetime
from sqlalchemy import Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class Ranking(Base):
    __tablename__ = "rankings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), unique=True)

    total_points: Mapped[int] = mapped_column(Integer, default=0)
    global_rank: Mapped[int] = mapped_column(Integer, default=0)
    level_rank: Mapped[int] = mapped_column(Integer, default=0)
    projects_completed: Mapped[int] = mapped_column(Integer, default=0)
    average_grade: Mapped[float] = mapped_column(Float, default=0.0)

    weekly_points: Mapped[int] = mapped_column(Integer, default=0)
    monthly_points: Mapped[int] = mapped_column(Integer, default=0)

    last_calculated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student: Mapped["Student"] = relationship("Student")
