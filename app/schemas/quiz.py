from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


# Question schemas
class QuestionCreate(BaseModel):
    text: str
    option_a: str
    option_b: str
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_answer: str  # A, B, C, D
    explanation: Optional[str] = None
    order: int = 0


class QuestionRead(BaseModel):
    id: int
    quiz_id: int
    text: str
    option_a: str
    option_b: str
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    order: int
    # correct_answer ko'rsatilmaydi studentga!
    model_config = ConfigDict(from_attributes=True)


class QuestionReadWithAnswer(QuestionRead):
    correct_answer: str
    explanation: Optional[str] = None


# Quiz schemas
class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    difficulty_level: str = "Beginner"
    time_limit_minutes: Optional[int] = None
    passing_score: int = 60
    points_reward: int = 0


class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[str] = None
    time_limit_minutes: Optional[int] = None
    passing_score: Optional[int] = None
    points_reward: Optional[int] = None
    is_active: Optional[bool] = None


class QuizRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    difficulty_level: str
    time_limit_minutes: Optional[int] = None
    passing_score: int
    points_reward: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class QuizReadWithQuestions(QuizRead):
    questions: List[QuestionRead] = []


# Student javob berish
class StudentAnswer(BaseModel):
    question_id: int
    answer: str  # A, B, C, D


class QuizSubmit(BaseModel):
    answers: List[StudentAnswer]
    time_spent_seconds: Optional[int] = None


# Natija
class QuizResultRead(BaseModel):
    id: int
    student_id: int
    quiz_id: int
    score: int
    correct_answers: int
    total_questions: int
    passed: bool
    time_spent_seconds: Optional[int] = None
    completed_at: datetime
    model_config = ConfigDict(from_attributes=True)