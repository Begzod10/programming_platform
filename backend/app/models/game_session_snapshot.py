"""Frozen record of a completed game session.

The live tables (game_sessions, game_questions, game_answers, game_teams)
capture state as it happens, but every relationship cascades on delete —
deleting a student, editing a question, or reshaping a team wipes the
historical picture. This snapshot table is written once at
complete_session() time and never mutated, so the teacher's post-game
summary view, CSV export, and parent-bot notification all read from a
single immutable source.

The payload is a JSON blob rather than a normalised sub-schema because
(a) it is written and read atomically, (b) the shape may evolve as we
add per-student stats, and (c) migrations for adding columns to child
tables would be pure friction — the source of truth stays the JSON
document produced by _build_snapshot_payload() in the endpoint layer.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Integer, DateTime, ForeignKey, JSON, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.team_game import GameSession
    from app.models.user import Student


class GameSessionSnapshot(Base):
    __tablename__ = "game_session_snapshots"
    __table_args__ = (
        UniqueConstraint("session_id", name="uq_game_session_snapshot_session"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False,
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    completed_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True,
    )
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    session: Mapped["GameSession"] = relationship("GameSession", foreign_keys=[session_id])
    completed_by_user: Mapped[Optional["Student"]] = relationship(
        "Student", foreign_keys=[completed_by],
    )
