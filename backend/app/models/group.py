from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, DateTime, func, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    price: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    gennis_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, unique=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    teacher_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True
    )

    students: Mapped[List["Student"]] = relationship(
        "Student",
        back_populates="group",
        cascade="all, delete-orphan",
        foreign_keys="Student.group_id"
    )

    teacher: Mapped[Optional["Student"]] = relationship(
        "Student",
        back_populates="managed_groups",
        foreign_keys="Group.teacher_id"
    )