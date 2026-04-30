from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import Student
    from .degree import Degree


class StudentDegree(Base):
    __tablename__ = "student_degrees"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    degree_id: Mapped[int] = mapped_column(ForeignKey("degrees.id", ondelete="CASCADE"), nullable=False)

    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    certificate_url: Mapped[str] = mapped_column(String(255), nullable=True)
    verification_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="student_degrees")
    degree: Mapped["Degree"] = relationship("Degree", back_populates="students")