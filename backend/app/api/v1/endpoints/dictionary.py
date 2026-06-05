from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List

from app.db.session import get_db
from app.models import Lesson
from app.models.dictionary import UserDictionary
from app.models.user import Student
from app.dependencies import get_current_student

from app.schemas.dictionary import (
    DictionaryCreate, DictionaryOut,
    QuizSessionOut, QuizAnswerIn, QuizResultOut, SessionCompleteOut, TodayQuizStatusOut,
    ReviewWordOut, ReviewAnswerIn, ReviewResultOut
)
from app.services import dictionary_service
from app.services.grok_service import explain_word_with_ai

router = APIRouter()


# ─── LUG'AT CRUD APILAR ──────────────────────────────────────

@router.post("/", response_model=DictionaryOut)
async def add_word(
        data: DictionaryCreate,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_student)
):
    safe_word = (data.word or "").strip()
    if not safe_word:
        raise HTTPException(status_code=422, detail="Word is required")
    if len(safe_word) > 80:
        safe_word = safe_word[:80]

    lesson_id = data.lesson_id
    if lesson_id:
        lesson = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
        if not lesson.scalar_one_or_none():
            lesson_id = None

    dup_q = select(UserDictionary).where(
        UserDictionary.student_id == current_user.id,
        func.lower(UserDictionary.word) == safe_word.lower(),
    )
    if lesson_id is None:
        dup_q = dup_q.where(UserDictionary.lesson_id.is_(None))
    else:
        dup_q = dup_q.where(UserDictionary.lesson_id == lesson_id)

    existing = (await db.execute(dup_q)).scalars().first()
    if existing:
        return existing

    # Context yo'q bo'lsa AI dan o'zbek tilidagi ta'rif olish
    context = data.context
    if not context:
        try:
            ai_result = await explain_word_with_ai(safe_word)
            context = ai_result.get("short_definition") or ai_result.get("definition") or ""
        except Exception:
            context = ""

    word = UserDictionary(
        student_id=current_user.id,
        word=safe_word,
        context=context,
        lesson_id=lesson_id,
    )
    db.add(word)
    await db.commit()
    await db.refresh(word)
    return word


@router.get("/", response_model=List[DictionaryOut])
async def get_my_dictionary(
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_student)
):
    result = await db.execute(
        select(UserDictionary).where(UserDictionary.student_id == current_user.id)
    )
    return result.scalars().all()


@router.delete("/{word_id}")
async def delete_word(
        word_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_student)
):
    result = await db.execute(
        select(UserDictionary).where(
            UserDictionary.id == word_id,
            UserDictionary.student_id == current_user.id
        )
    )
    word = result.scalar_one_or_none()
    if not word:
        raise HTTPException(status_code=404, detail="Topilmadi")
    await db.delete(word)
    await db.commit()
    return {"message": "O'chirildi"}


@router.post("/explain")
async def explain_word(
        data: DictionaryCreate,
        current_user: Student = Depends(get_current_student),
):
    """Grok yoki OpenAI orqali so'zga sun'iy intellekt ta'rifini olish"""
    return await explain_word_with_ai(data.word)


# ─── MINI QUIZ APILAR (DRAG & DROP) ─────────────────────

@router.get("/quiz/status", response_model=TodayQuizStatusOut)
async def get_today_quiz_status(
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_student)
):
    """Bugun nechta o'yin qoldi va natijalari qandayligini ko'rish"""
    return await dictionary_service.get_quiz_status(current_user.id, db)


@router.post("/quiz/start", response_model=QuizSessionOut)
async def start_quiz(
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_student)
):
    """Yangi o'yin boshlash va 5 ta tasodifiy so'z/ma'noni olish"""
    return await dictionary_service.start_quiz_session(current_user.id, db)


@router.post("/quiz/answer", response_model=QuizResultOut)
async def quiz_submit_answer(
        data: QuizAnswerIn,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_student)
):
    """O'quvchi drag qilib drop qilgan har bir javobni yuborishi"""
    return await dictionary_service.submit_answer(
        session_id=data.session_id,
        word_id=data.word_id,
        placed_meaning_id=data.placed_meaning_id,
        student_id=current_user.id,
        db=db
    )


@router.post("/quiz/complete/{session_id}", response_model=SessionCompleteOut)
async def quiz_complete_session(
        session_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_student)
):
    """5 ta so'z tugagandan so'ng seansni yakunlash va ochkoni hisoblash"""
    return await dictionary_service.complete_session(session_id, current_user.id, db)


# ─── KUNLIK TAKRORLASH APILAR (SWIPE & AI) ─────────

@router.get("/review/words", response_model=List[ReviewWordOut])
async def get_words_for_review(
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_student)
):
    """O'quvchiga o'z lug'atidan ma'nosiz so'zlar ro'yxatini yuklab berish (Swipe boshlash)"""
    return await dictionary_service.get_review_words(current_user.id, db)


@router.post("/review/check", response_model=ReviewResultOut)
async def check_review_answer(
        data: ReviewAnswerIn,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_student)
):
    """O'quvchi qo'lda yozgan ma'noni AI orqali tekshirish va fikrini olish"""
    return await dictionary_service.check_review(
        word_id=data.word_id,
        user_meaning=data.user_meaning,
        student_id=current_user.id,
        db=db
    )
