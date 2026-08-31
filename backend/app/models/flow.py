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

    Deliberately has no price: unlike Group this isn't a billing unit. It DOES
    have teacher_id — a turon teacher can be reachable ONLY through a flow
    (e.g. a subject teacher scheduled to a flow rather than a group in the
    timetable), so without it that teacher would sync zero students at all.
    See GennisService.sync_teacher_data / _sync_flow."""
    __tablename__ = "flows"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    turon_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, unique=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    teacher_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True
    )

    students: Mapped[List["Student"]] = relationship(
        "Student",
        secondary=student_flows,
        back_populates="flows",
        lazy="selectin"
    )

    teacher: Mapped[Optional["Student"]] = relationship(
        "Student",
        back_populates="managed_flows",
        foreign_keys="Flow.teacher_id"
    )
