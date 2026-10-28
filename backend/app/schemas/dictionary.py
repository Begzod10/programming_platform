from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─── LUG'AT SHÉMALARI ─────────────────────────────────

class DictionaryCreate(BaseModel):
    word: str = Field(
        ..., min_length=1, max_length=80,
        description="Lug'atga qo'shilayotgan so'z yoki qisqa ibora (1-6 ta so'z, 80 belgigacha)",
    )
    context: Optional[str] = Field(None, description="So'zning ma'nosi yoki tarjimasi")
    lesson_id: Optional[int] = None
    lang: Optional[str] = Field(None, description="Foydalanuvchi tili: 'uz' yoki 'ru'")


class DictionaryOut(BaseModel):
    id: int
    word: str
    context: Optional[str]
    lesson_id: Optional[int] = None
    lesson_title: Optional[str] = None
    course_id: Optional[int] = None
    course_title: Optional[str] = None
    review_count: int
    correct_count: int
    incorrect_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class TeacherDictionaryWord(BaseModel):
    """One saved word as the teacher sees it (read-only): enough to ask the student the word out loud."""
    id: int
    word: str
    context: Optional[str] = None
    lang: str = "uz"
    lesson_id: Optional[int] = None
    lesson_title: Optional[str] = None
    course_id: Optional[int] = None
    course_title: Optional[str] = None
    review_count: int = 0
    correct_count: int = 0
    incorrect_count: int = 0
    last_reviewed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    # the teacher's oral checks of this word: the latest verdict (None = never asked), when, and how many times asked
    last_check_knows: Optional[bool] = None
    last_checked_at: Optional[datetime] = None
    checks_count: int = 0


class TeacherStudentDictionary(BaseModel):
    student_id: int
    total: int
    known: int = 0          # words whose latest check says "knows"
    unknown: int = 0        # latest check says "does not know"
    unchecked: int = 0      # never asked
    words: List[TeacherDictionaryWord]


class TeacherWordCheckBody(BaseModel):
    knows: bool


# ─── QUIZ (DRAG AND DROP) SHÉMALARI ───────────────────

class QuizWordItem(BaseModel):
    id: int
    word: str


class QuizMeaningItem(BaseModel):
    id: int  # Bu aslida word_id bo'ladi, frontend drag-drop mosligini tekshirish uchun ishlatadi
    meaning: str


class QuizSessionOut(BaseModel):
    session_id: int
    session_number: int
    words: List[QuizWordItem]  # Faqat so'zlar ro'yxati (aralash)
    meanings: List[QuizMeaningItem]  # Faqat ma'nolar ro'yxati (boshqa tartibda aralash)
    score: int
    is_completed: bool


class QuizAnswerIn(BaseModel):
    session_id: int
    word_id: int
    placed_meaning_id: int  # Talaba moslashtirgan ma'noning id-si


class QuizResultOut(BaseModel):
    session_id: int
    is_correct: bool
    correct_meaning_id: int
    score_earned: int
    total_score: int


class SessionCompleteOut(BaseModel):
    session_id: int
    total_score: int
    correct_answers: int
    total_words: int
    is_completed: bool


class QuizShortStatus(BaseModel):
    id: int
    session_number: int
    score: int
    is_completed: bool


class TodayQuizStatusOut(BaseModel):
    played_today: int
    remaining_today: int
    sessions: List[QuizShortStatus]


# ─── KUNLIK TAKRORLASH (AI SWIPE) SHÉMALARI ─────────

class ReviewWordOut(BaseModel):
    id: int
    word: str


class ReviewAnswerIn(BaseModel):
    word_id: int
    user_meaning: str


class ReviewResultOut(BaseModel):
    word_id: int
    word: str
    is_correct: bool
    correct_meaning: str
    ai_feedback: str
