from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, DateTime, func, Integer, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


student_groups = Table(
    "student_groups",
    Base.metadata,
    Column("student_id", ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True
)


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # NOT unique: class names like "1-blue"/"4-green" are short room/cohort
    # labels reused across branches — turon_id/gennis_id (below) are the
    # actual identity _sync_group looks rows up by. Was unique=True until a
    # branch-wide teacher sync (see gennis_service.py's
    # _teaches_student_platform_subject) hit two different branches' real
    # "4-green" groups in the same login and 500'd on insert (turon_id 188
    # vs 684, 2026-09-03) — dropped live in prod, this migration makes it
    # permanent.
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    price: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    gennis_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, unique=True)
    # Kept separate from gennis_id for the same reason as Student.turon_id —
    # gennis and turon group ids are independent, overlapping numeric spaces.
    turon_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, unique=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    teacher_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True
    )

    students: Mapped[List["Student"]] = relationship(
        "Student",
        secondary=student_groups,
        back_populates="groups",
        lazy="selectin"
    )

    teacher: Mapped[Optional["Student"]] = relationship(
        "Student",
        back_populates="managed_groups",
        foreign_keys="Group.teacher_id"
    )