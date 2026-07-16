"""Audit ledger for manual /rankings/(add|subtract)-points calls.

Every other point-awarding path (exercise submissions, project.points_earned,
lesson.points_reward, achievement.points_reward) is reconstructable from
source-of-truth rows. Manual teacher/admin adjustments were not — they mutated
students.total_points and disappeared. This ledger closes that gap so the
recalc script in scripts/recalc_points.py can verify:

    students.total_points ==
        SUM(exercise.points where submission scored)
      + SUM(project.points_earned where Approved)
      + SUM(lesson.points_reward where completed)
      + SUM(achievement.points_reward where earned)
      + SUM(point_adjustments.delta)   <-- this table

Historical manual adjustments (pre-ledger) show as drift, which is correct.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import Student


class PointAdjustment(Base):
    """One row per manual add-points / subtract-points call.

    `delta` is signed: positive for add-points, negative for subtract-points.
    `actor_id` is the teacher/admin who initiated the change (from
    get_current_instructor). `reason` is required at the API layer so the
    audit trail always carries context.
    """

    __tablename__ = "point_adjustments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    actor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True,
    )
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    related_entity_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    related_entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )

    student: Mapped["Student"] = relationship(
        "Student", foreign_keys=[student_id],
    )
    actor: Mapped[Optional["Student"]] = relationship(
        "Student", foreign_keys=[actor_id],
    )

    def __repr__(self) -> str:
        return (
            f"<PointAdjustment(student_id={self.student_id}, delta={self.delta}, "
            f"actor_id={self.actor_id})>"
        )
