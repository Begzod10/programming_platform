from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional, List
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Enum, UniqueConstraint, JSON, Boolean, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


def utcnow():
    return datetime.now(timezone.utc)


class GameType(str, PyEnum):
    team       = "team"
    individual = "individual"


class SessionStatus(str, PyEnum):
    pending   = "pending"
    active    = "active"
    completed = "completed"


class QuestionStatus(str, PyEnum):
    pending  = "pending"
    active   = "active"
    revealed = "revealed"


class GameSession(Base):
    __tablename__ = "game_sessions"

    id:                  Mapped[int]           = mapped_column(primary_key=True, autoincrement=True)
    title:               Mapped[str]           = mapped_column(String(255), nullable=False)
    description:         Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    game_type:           Mapped[str]           = mapped_column(String(50), nullable=False)
    status:              Mapped[SessionStatus] = mapped_column(Enum(SessionStatus), default=SessionStatus.pending, nullable=False)
    language:            Mapped[str]           = mapped_column(String(2), default='uz', nullable=False)
    auto_mode:           Mapped[bool]          = mapped_column(Boolean, default=False, nullable=False)
    course_id:           Mapped[Optional[int]] = mapped_column(ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    created_by:          Mapped[int]           = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    team_count:          Mapped[int]           = mapped_column(Integer, default=2, nullable=False)
    current_question_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at:          Mapped[datetime]      = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at:          Mapped[datetime]      = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    teams:     Mapped[List["GameTeam"]]      = relationship("GameTeam", back_populates="session", cascade="all, delete-orphan")
    questions: Mapped[List["GameQuestion"]]  = relationship("GameQuestion", back_populates="session", cascade="all, delete-orphan", order_by="GameQuestion.order_index")
    course:    Mapped[Optional["Course"]]    = relationship("Course",  foreign_keys=[course_id])
    creator:   Mapped[Optional["Student"]]   = relationship("Student", foreign_keys=[created_by])


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


class GameQuestion(Base):
    __tablename__ = "game_questions"

    id:             Mapped[int]            = mapped_column(primary_key=True, autoincrement=True)
    session_id:     Mapped[int]            = mapped_column(ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False)
    question_text:    Mapped[str]            = mapped_column(Text, nullable=False)
    question_text_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    options:          Mapped[list]          = mapped_column(JSON, nullable=False)  # list of strings (4 for quiz; bug_hunt: candidate line numbers as strings)
    options_ru:       Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # RU variants, same order/length as options
    correct_option: Mapped[int]            = mapped_column(Integer, nullable=False)  # 0-indexed
    time_limit:     Mapped[int]            = mapped_column(Integer, default=30, nullable=False)  # seconds
    points:         Mapped[int]            = mapped_column(Integer, default=1000, nullable=False)
    order_index:    Mapped[int]            = mapped_column(Integer, default=0, nullable=False)
    status:         Mapped[QuestionStatus] = mapped_column(Enum(QuestionStatus), default=QuestionStatus.pending, nullable=False)
    activated_at:   Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at:     Mapped[datetime]       = mapped_column(DateTime(timezone=True), default=utcnow)

    # ── Bug-hunt kind ──────────────────────────────────────────────────
    # question_kind='quiz' (default) leaves every column below NULL and the
    # existing options/correct_option pipeline untouched. 'bug_hunt' reuses
    # that same pipeline: options holds candidate line numbers as strings
    # (e.g. ["3","7","12"]) and correct_option indexes the buggy one — the
    # code snippet stays the single source of truth for option *text*.
    question_kind:      Mapped[str]           = mapped_column(String(20), default="quiz", nullable=False)
    code_snippet:        Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code_language:       Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bug_line:             Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-indexed
    bug_explanation:      Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # shown on reveal
    bug_explanation_ru:   Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    session: Mapped["GameSession"]      = relationship("GameSession", back_populates="questions")
    answers: Mapped[List["GameAnswer"]] = relationship("GameAnswer", back_populates="question", cascade="all, delete-orphan")


class StudentQuestionOrder(Base):
    __tablename__ = "student_question_orders"
    __table_args__ = (UniqueConstraint("session_id", "student_id", name="uq_student_question_order"),)

    id:           Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    session_id:   Mapped[int]      = mapped_column(ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False)
    student_id:   Mapped[int]      = mapped_column(ForeignKey("students.id",     ondelete="CASCADE"), nullable=False)
    question_ids: Mapped[list]     = mapped_column(JSON, nullable=False)  # shuffled list of question IDs


class GameAnswer(Base):
    __tablename__ = "game_answers"
    __table_args__ = (UniqueConstraint("question_id", "student_id", name="uq_game_answer"),)

    id:             Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    question_id:    Mapped[int]      = mapped_column(ForeignKey("game_questions.id", ondelete="CASCADE"), nullable=False)
    student_id:     Mapped[int]      = mapped_column(ForeignKey("students.id",       ondelete="CASCADE"), nullable=False)
    team_id:        Mapped[int]      = mapped_column(ForeignKey("game_teams.id",     ondelete="CASCADE"), nullable=False)
    chosen_option:  Mapped[int]      = mapped_column(Integer, nullable=False)  # 0-indexed
    is_correct:     Mapped[bool]     = mapped_column(Boolean, nullable=False)
    points_earned:  Mapped[int]      = mapped_column(Integer, default=0, nullable=False)
    answered_at:    Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    question: Mapped["GameQuestion"] = relationship("GameQuestion", back_populates="answers")
    student:  Mapped["Student"]      = relationship("Student", foreign_keys=[student_id])
    team:     Mapped["GameTeam"]     = relationship("GameTeam", foreign_keys=[team_id])
