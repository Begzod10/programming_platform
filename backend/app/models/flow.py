from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, DateTime, func, Integer, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


student_flows = Table(
    "student_flows",
    Base.metadata,
    Column("student_id", ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("flow_id", ForeignKey("flows.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True
)


class Flow(Base):
    """A turon student's second, independent container — NOT derived from
    Group membership (see gennis-v2's student_platform_login shim). Gennis has
    no equivalent concept, so this table only ever holds turon_id rows.

    Deliberately has no price/teacher_id: unlike Group this isn't a billing
    unit, and teacher-side flow sync isn't wired up (nothing populates it —
    see GennisService.sync_teacher_data)."""
    __tablename__ = "flows"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    turon_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, unique=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    students: Mapped[List["Student"]] = relationship(
        "Student",
        secondary=student_flows,
        back_populates="flows",
        lazy="selectin"
    )
