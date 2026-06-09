from typing import Optional
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
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

    student = relationship("Student", back_populates="dictionary_words")
    lesson = relationship("Lesson", back_populates="user_dictionaries")


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
