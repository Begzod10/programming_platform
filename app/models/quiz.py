from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty_level: Mapped[str] = mapped_column(String(20), default="Beginner")  # Beginner/Intermediate/Advanced
    time_limit_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # vaqt cheklov
    passing_score: Mapped[int] = mapped_column(Integer, default=60)  # o'tish bali (%)
    points_reward: Mapped[int] = mapped_column(Integer, default=0)  # o'tganda beriladigan ball
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    questions: Mapped[List["Question"]] = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    results: Mapped[List["StudentQuizResult"]] = relationship("StudentQuizResult", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)  # savol matni
    option_a: Mapped[str] = mapped_column(Text, nullable=False)
    option_b: Mapped[str] = mapped_column(Text, nullable=False)
    option_c: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    option_d: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    correct_answer: Mapped[str] = mapped_column(String(1), nullable=False)  # A, B, C yoki D
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # tushuntirish
    order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")


class StudentQuizResult(Base):
    __tablename__ = "student_quiz_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0)  # foizda
    correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped["Student"] = relationship("Student")
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="results")