from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List

from app.db.session import get_db
from app.models import Lesson
from app.models.course import Course
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
    # Strip outer whitespace and any trailing punctuation a careless mouse
    # selection might have grabbed (period, comma, semicolon, etc.).
    safe_word = (data.word or "").strip().strip(".,!?;:•·«»\"'()[]{}—–-")
    if not safe_word:
        raise HTTPException(status_code=422, detail="So'z bo'sh bo'lishi mumkin emas")

    # Dictionary entries are meant to be a word or a tight phrase, not a
    # whole sentence. Enforce both a length cap and a max word count so a
    # caller that bypasses the frontend popup can't pollute the vocabulary
    # with sentence-sized rows.
    if len(safe_word) > 40:
        raise HTTPException(
            status_code=422,
            detail="Lug'atga faqat qisqa so'z yoki ibora qo'shing (40 belgi gacha).",
        )
    if len(safe_word.split()) > 3:
        raise HTTPException(
            status_code=422,
            detail="Lug'atga 3 ta so'zdan ko'pini qo'shib bo'lmaydi.",
        )

    lesson_id = data.lesson_id
    lesson_obj: Lesson | None = None
    course_title = ""
    if lesson_id:
        lesson_obj = (
            await db.execute(select(Lesson).where(Lesson.id == lesson_id))
        ).scalar_one_or_none()
        if not lesson_obj:
            lesson_id = None
        elif lesson_obj.course_id:
            course_row = (
                await db.execute(
                    select(Course.title).where(Course.id == lesson_obj.course_id)
                )
            ).scalar_one_or_none()
            if course_row:
                course_title = course_row

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

    # Context yo'q bo'lsa AI dan o'zbek tilidagi ta'rif olish.
    # Lesson + course title are passed as scope hints so the model returns
    # the sense that fits the lesson — "Panel" in a JS lesson is the DevTools
    # panel, not a generic sidebar.
    context = data.context
    if not context:
        try:
            ai_result = await explain_word_with_ai(
                safe_word,
                course_title=course_title,
                lesson_title=(lesson_obj.title if lesson_obj else ""),
                lesson_excerpt=(
                    (lesson_obj.text_content or "")[:400] if lesson_obj else ""
                ),
            )
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
