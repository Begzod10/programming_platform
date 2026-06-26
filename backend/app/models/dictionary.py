from typing import Optional
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float, JSON
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime
from app.db.base_class import Base


class UserDictionary(Base):
    __tablename__ = "user_dictionary"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    word = Column(String(80), nullable=False)
    context = Column(String, nullable=True)
    lesson_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    review_count = Column(Integer, default=0, nullable=False)
    last_reviewed_at = Column(DateTime, nullable=True)
    correct_count = Column(Integer, default=0, nullable=False)
    incorrect_count = Column(Integer, default=0, nullable=False)

    # Language of the definition ('uz' or 'ru'). One entry per (student, word, lang).
    lang = Column(String(4), nullable=False, server_default="uz", default="uz")

    # AI-extracted grammatical category — nullable since old rows pre-date
    # this and not every entry maps cleanly (code identifiers, phrases).
    part_of_speech = Column(String(40), nullable=True)

    # SM-2 spaced-repetition state (ported from life_tracker). Defaults
    # match srs.DEFAULT_EASE so existing rows behave like a brand-new card
    # once the migration runs and backfills the columns with the defaults.
    ease_factor = Column(Float, default=2.5, nullable=False, server_default="2.5")
    interval_days = Column(Integer, default=0, nullable=False, server_default="0")
    reps = Column(Integer, default=0, nullable=False, server_default="0")
    lapses = Column(Integer, default=0, nullable=False, server_default="0")
    next_review_at = Column(DateTime, nullable=True, index=True)

    student = relationship("Student", back_populates="dictionary_words")
    lesson = relationship("Lesson", back_populates="user_dictionaries")


class PracticeSession(Base):
    """One Mashq session — created when the user picks a mode, finalised
    when they finish (or abandoned via DELETE).

    `progress` stores the per-mode in-flight state so a student can close
    the tab and resume where they left off (chunk index, answered word ids,
    sub-mode within Quiz+, etc.). It's an opaque JSON blob the frontend
    owns the schema of; the backend just passes it through.
    """

    __tablename__ = "dict_practice_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(
        Integer,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mode = Column(String(20), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    total_words = Column(Integer, default=0, nullable=False)
    correct = Column(Integer, default=0, nullable=False)
    progress = Column(JSON, nullable=True)

    student = relationship("Student")


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    session_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    session_number = Column(Integer, nullable=False)
    score = Column(Integer, default=0, nullable=False)
    total_words = Column(Integer, default=5, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    student = relationship("Student")
    answers = relationship("QuizAnswer", back_populates="session", cascade="all, delete-orphan")


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("quiz_sessions.id", ondelete="CASCADE"), nullable=False)
    word_id = Column(Integer, ForeignKey("user_dictionary.id", ondelete="CASCADE"), nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    answered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("QuizSession", back_populates="answers")
    word = relationship("UserDictionary")
