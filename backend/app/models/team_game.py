from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional, List
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


def utcnow():
    return datetime.now(timezone.utc)


class GameType(str, PyEnum):
    quiz    = "quiz"
    coding  = "coding"
    project = "project"
    custom  = "custom"


class SessionStatus(str, PyEnum):
    pending   = "pending"
    active    = "active"
    completed = "completed"


class GameSession(Base):
    __tablename__ = "game_sessions"

    id:          Mapped[int]           = mapped_column(primary_key=True, autoincrement=True)
    title:       Mapped[str]           = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    game_type:   Mapped[GameType]      = mapped_column(Enum(GameType), nullable=False)
    status:      Mapped[SessionStatus] = mapped_column(Enum(SessionStatus), default=SessionStatus.pending, nullable=False)
    course_id:   Mapped[Optional[int]] = mapped_column(ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    created_by:  Mapped[int]           = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    team_count:  Mapped[int]           = mapped_column(Integer, default=2, nullable=False)
    created_at:  Mapped[datetime]      = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at:  Mapped[datetime]      = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    teams:   Mapped[List["GameTeam"]]     = relationship("GameTeam", back_populates="session", cascade="all, delete-orphan")
    course:  Mapped[Optional["Course"]]   = relationship("Course",  foreign_keys=[course_id])
    creator: Mapped[Optional["Student"]]  = relationship("Student", foreign_keys=[created_by])


class GameTeam(Base):
    __tablename__ = "game_teams"

    id:         Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int]      = mapped_column(ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False)
    name:       Mapped[str]      = mapped_column(String(100), nullable=False)
    color:      Mapped[str]      = mapped_column(String(7), default="#3498db", nullable=False)
    score:      Mapped[int]      = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    session: Mapped["GameSession"]          = relationship("GameSession", back_populates="teams")
    members: Mapped[List["GameTeamMember"]] = relationship("GameTeamMember", back_populates="team", cascade="all, delete-orphan")


class GameTeamMember(Base):
    __tablename__ = "game_team_members"
    __table_args__ = (UniqueConstraint("team_id", "student_id", name="uq_game_team_member"),)

    id:         Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    team_id:    Mapped[int]      = mapped_column(ForeignKey("game_teams.id",   ondelete="CASCADE"), nullable=False)
    student_id: Mapped[int]      = mapped_column(ForeignKey("students.id",     ondelete="CASCADE"), nullable=False)
    joined_at:  Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    team:    Mapped["GameTeam"]    = relationship("GameTeam", back_populates="members")
    student: Mapped["Student"]     = relationship("Student",  foreign_keys=[student_id])
