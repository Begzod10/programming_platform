import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional

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

    # Dictionary entries are meant to be a word, a tight phrase, or a short
    # programming-glossary line (e.g. `<a> — Giperhavola (Link)`). The
    # length cap and word count keep callers that bypass the lesson popup
    # from polluting the vocabulary with sentence-sized rows, but the
    # ceilings are tuned for glossary entries — not for the much stricter
    # auto-selection popup, which still enforces its own 40-char / 3-word
    # limit because there the user might have selected accidentally.
    if len(safe_word) > 80:
        raise HTTPException(
            status_code=422,
            detail="Lug'atga faqat qisqa so'z yoki ibora qo'shing (80 belgi gacha).",
        )
    if len(safe_word.split()) > 6:
        raise HTTPException(
            status_code=422,
            detail="Lug'atga 6 ta so'zdan ko'pini qo'shib bo'lmaydi.",
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

    # Dedup per (student, word, lang) — same word can exist in 'uz' and 'ru'.
    entry_lang = (data.lang or "uz").strip().lower() or "uz"
    dup_q = select(UserDictionary).where(
        UserDictionary.student_id == current_user.id,
        func.lower(UserDictionary.word) == safe_word.lower(),
        UserDictionary.lang == entry_lang,
    )
    existing = (await db.execute(dup_q)).scalars().first()
    if existing:
        return existing

    # Always call AI to generate a proper definition in the user's language.
    # data.context (sentence extracted by the popup) is used as a scope hint
    # for the AI — NOT stored directly as the definition.
    context = ""
    part_of_speech = None
    try:
        # Best excerpt: the popup's extracted sentence (exact context of use).
        # Fallback: lesson text_content stripped of HTML/mermaid blocks.
        if data.context and data.context.strip():
            excerpt = data.context.strip()[:300]
        else:
            raw_text = (lesson_obj.text_content or "") if lesson_obj else ""
            clean_text = re.sub(r"<pre[\s\S]*?</pre>", " ", raw_text, flags=re.IGNORECASE)
            clean_text = re.sub(r"```[\s\S]*?```", " ", clean_text)
            clean_text = re.sub(r"<[^>]+>", " ", clean_text)
            excerpt = re.sub(r"\s+", " ", clean_text).strip()[:300]

        ai_result = await explain_word_with_ai(
            safe_word,
            course_title=course_title,
            lesson_title=(lesson_obj.title if lesson_obj else ""),
            lesson_excerpt=excerpt,
            lang=data.lang or "uz",
        )
        context = ai_result.get("short_definition") or ai_result.get("definition") or ""
        pos_raw = (ai_result.get("part_of_speech") or "").strip().lower()
        if pos_raw and len(pos_raw) <= 40:
            part_of_speech = pos_raw
    except Exception:
        context = ""

    word = UserDictionary(
        student_id=current_user.id,
        word=safe_word,
        context=context,
        lesson_id=lesson_id,
        part_of_speech=part_of_speech,
        lang=entry_lang,
    )
    db.add(word)
    await db.commit()
    await db.refresh(word)
    return word


@router.get("/", response_model=List[DictionaryOut])
async def get_my_dictionary(
        lang: Optional[str] = None,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_student)
):
    """Return saved words for the current student, filtered by lang.

    The frontend passes ?lang=uz or ?lang=ru so each language session shows
    only the words saved in that language.
    """
    q = (
        select(
            UserDictionary,
            Lesson.title.label("lesson_title"),
            Lesson.course_id.label("course_id"),
            Course.title.label("course_title"),
        )
        .outerjoin(Lesson, Lesson.id == UserDictionary.lesson_id)
        .outerjoin(Course, Course.id == Lesson.course_id)
        .where(UserDictionary.student_id == current_user.id)
    )
    if lang:
        q = q.where(UserDictionary.lang == lang.strip().lower())
    q = q.order_by(UserDictionary.created_at.desc())
    rows = (await db.execute(q)).all()

    out: List[DictionaryOut] = []
    for word, lesson_title, course_id, course_title in rows:
        out.append(DictionaryOut(
            id=word.id,
            word=word.word,
            context=word.context,
            lesson_id=word.lesson_id,
            lesson_title=lesson_title,
            course_id=course_id,
            course_title=course_title,
            review_count=word.review_count,
            correct_count=word.correct_count,
            incorrect_count=word.incorrect_count,
            created_at=word.created_at,
        ))
    return out


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
    result = await dictionary_service.complete_session(session_id, current_user.id, db)
    try:
        from app.services.streak_service import bump_streak
        await bump_streak(db, current_user.id)
        await db.commit()
    except Exception:
        await db.rollback()
    return result


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
