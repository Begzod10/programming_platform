from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.utils.datetime_utils import utcnow


class TeacherPenalty(Base):
    """One row per manual penalty a teacher applies to a student.

    A penalty docks ``amount`` points from the student's *profile* total via
    RankingService.revoke_earned_points (floored at 0) — it reduces both the
    spendable wallet and the career/leaderboard total (Ranking.total_points),
    which is exactly the "rating points" the student sees. It is NOT tied to any
    project or lesson; it is a standalone disciplinary action.

    The row is the audit trail: who penalised whom, how much, for what reason,
    and the student's balance immediately before/after. ``teacher_id`` is
    SET NULL on teacher deletion so history survives, and the whole row is
    CASCADE-deleted with the student (consistent with the rest of the schema).
    """
    __tablename__ = "teacher_penalties"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Teachers are Student rows (role=instructor). SET NULL keeps the audit
    # trail if the teacher account is later removed.
    teacher_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Points docked (always positive). Uncapped — a teacher may fine any amount.
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    # One of the PENALTY_TYPES keys below (free-form fallback = "other").
    penalty_type: Mapped[str] = mapped_column(String(40), nullable=False, default="other")
    # Optional free-text note the teacher adds ("за что").
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Student's career/leaderboard total immediately before and after the dock
    # (after is floored at 0), for the history view.
    points_before: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    points_after: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )

    __table_args__ = (
        Index("ix_teacher_penalties_student_created", "student_id", "created_at"),
    )

    def __repr__(self) -> str:
        return (f"<TeacherPenalty(id={self.id}, student={self.student_id}, "
                f"amount={self.amount}, type={self.penalty_type})>")


# Canonical penalty types. The frontend renders localized labels + icons from
# these keys; the backend only validates membership (unknown → "other").
PENALTY_TYPES = (
    "rule_violation",   # 🚫 Нарушение правил
    "ai_abuse",         # 🤖 Злоупотребление ИИ / читерство
    "plagiarism",       # 📋 Плагиат
    "missed_deadline",  # ⏰ Срыв дедлайна
    "inactivity",       # 😴 Неактивность
    "behavior",         # 🗣 Поведение
    "other",            # ✏️ Другое
)
