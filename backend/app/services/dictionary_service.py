from sqlalchemy import cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
from typing import List
import random
from fastapi import HTTPException

from app.models.dictionary import UserDictionary, QuizSession, QuizAnswer
from app.schemas.dictionary import (
    QuizSessionOut, QuizWordItem, QuizMeaningItem,
    SessionCompleteOut, QuizResultOut, TodayQuizStatusOut, QuizShortStatus,
    ReviewWordOut, ReviewResultOut
)
from app.services.grok_service import check_word_meaning_with_ai

QUIZ_WORDS_COUNT = 5
QUIZ_DAILY_LIMIT = 2
QUIZ_SCORE_PER_CORRECT = 10

async def get_today_sessions(student_id: int, db: AsyncSession) -> List[QuizSession]:
    """Foydalanuvchining bugungi UTC bo'yicha o'yinlar seansini olish"""
    today_utc = datetime.now(timezone.utc).date()
    q = select(QuizSession).where(
        QuizSession.student_id == student_id,
        cast(QuizSession.session_date, Date) == today_utc,
    )
    result = await db.execute(q)
    return result.scalars().all()

async def get_quiz_status(student_id: int, db: AsyncSession) -> TodayQuizStatusOut:
    """Kunlik o'yinlar statusini aniqlash"""
    today_sessions = await get_today_sessions(student_id, db)
    played = len(today_sessions)
    remaining = max(0, QUIZ_DAILY_LIMIT - played)

    sessions_list = [
        QuizShortStatus(
            id=s.id,
            session_number=s.session_number,
            score=s.score,
            is_completed=s.is_completed
        ) for s in today_sessions
    ]
    return TodayQuizStatusOut(played_today=played, remaining_today=remaining, sessions=sessions_list)

async def start_quiz_session(student_id: int, db: AsyncSession) -> QuizSessionOut:
    """Yangi Drag and Drop o'yin seansini boshlash"""
    today_sessions = await get_today_sessions(student_id, db)

    if len(today_sessions) >= QUIZ_DAILY_LIMIT:
        raise HTTPException(status_code=400, detail="Bugun uchun 2 ta quiz o'yini bajarildi. Ertaga qayta keling!")

    # Faqat ma'nosi (context) bor so'zlarni eng kam takrorlangan 20 tasini saralab olish
    words_q = select(UserDictionary).where(
        UserDictionary.student_id == student_id,
        UserDictionary.context.isnot(None),
        UserDictionary.context != ""
    ).order_by(UserDictionary.review_count.asc()).limit(20)

    all_words = (await db.execute(words_q)).scalars().all()

    if len(all_words) < QUIZ_WORDS_COUNT:
        raise HTTPException(
            status_code=400,
            detail=f"Quiz uchun kamida {QUIZ_WORDS_COUNT} ta ma'noli so'z kerak. Hozir lug'atingizda {len(all_words)} ta so'z bor."
        )

    selected_words = random.sample(all_words, QUIZ_WORDS_COUNT)

    session_number = len(today_sessions) + 1
    session = QuizSession(
        student_id=student_id,
        session_date=datetime.now(timezone.utc),
        session_number=session_number,
        total_words=QUIZ_WORDS_COUNT,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # So'zlar va Ma'nolarni frontend bilib qolmasligi uchun alohida ob'ekt qilib aralashtiramiz
    words_shuffled = [QuizWordItem(id=w.id, word=w.word) for w in selected_words]
    meanings_shuffled = [QuizMeaningItem(id=w.id, meaning=w.context) for w in selected_words]

    random.shuffle(words_shuffled)
    random.shuffle(meanings_shuffled)

    return QuizSessionOut(
        session_id=session.id,
        session_number=session_number,
        words=words_shuffled,
        meanings=meanings_shuffled,
        score=0,
        is_completed=False,
    )

async def submit_answer(
    session_id: int,
    word_id: int,
    placed_meaning_id: int,
    student_id: int,
    db: AsyncSession,
) -> QuizResultOut:
    """Har bir moslashtirilgan elementni tekshirish va saqlash"""
    session_q = select(QuizSession).where(
        QuizSession.id == session_id,
        QuizSession.student_id == student_id,
    )
    session = (await db.execute(session_q)).scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Sessiya topilmadi")
    if session.is_completed:
        raise HTTPException(status_code=400, detail="Bu sessiya allaqachon yakunlangan")

    word_q = select(UserDictionary).where(
        UserDictionary.id == word_id,
        UserDictionary.student_id == student_id,
    )
    word = (await db.execute(word_q)).scalar_one_or_none()
    if not word:
        raise HTTPException(status_code=404, detail="So'z topilmadi")

    # Agar o'quvchi to'g'ri bog'lagan bo'lsa word_id va placed_meaning_id teng bo'ladi
    is_correct = (word_id == placed_meaning_id)
    score_earned = QUIZ_SCORE_PER_CORRECT if is_correct else 0

    # Javobni tarixga yozamiz
    db.add(QuizAnswer(
        session_id=session.id,
        word_id=word_id,
        is_correct=is_correct,
        answered_at=datetime.now(timezone.utc),
    ))

    # Statistikani yangilash
    if is_correct:
        session.correct_answers += 1
        session.score += score_earned
        word.correct_count += 1
    else:
        word.incorrect_count += 1

    await db.commit()
    await db.refresh(session)

    return QuizResultOut(
        session_id=session.id,
        is_correct=is_correct,
        correct_meaning_id=word_id,
        score_earned=score_earned,
        total_score=session.score,
    )

async def complete_session(session_id: int, student_id: int, db: AsyncSession) -> SessionCompleteOut:
    """O'yin tugaganda seansni yopish"""
    session_q = select(QuizSession).where(
        QuizSession.id == session_id,
        QuizSession.student_id == student_id,
    )
    session = (await db.execute(session_q)).scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Sessiya topilmadi")
    if session.is_completed:
        raise HTTPException(status_code=400, detail="Sessiya allaqachon yakunlangan")

    session.is_completed = True
    session.completed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(session)

    return SessionCompleteOut(
        session_id=session.id,
        total_score=session.score,
        correct_answers=session.correct_answers,
        total_words=session.total_words,
        is_completed=True,
    )

# ─── REVIEW LOGIKASI (AI SWIPE) ─────────────────────────

async def get_review_words(student_id: int, db: AsyncSession) -> List[ReviewWordOut]:
    """Takrorlash uchun eski va kam ko'rilgan so'zlarni tartiblab berish"""
    q = select(UserDictionary).where(
        UserDictionary.student_id == student_id,
    ).order_by(
        UserDictionary.review_count.asc(),
        UserDictionary.created_at.asc(),
    )
    words = (await db.execute(q)).scalars().all()
    if not words:
        raise HTTPException(status_code=404, detail="Lug'atingizda hech qanday so'z yo'q. Avval so'z qo'shing.")
    return [ReviewWordOut(id=w.id, word=w.word) for w in words]

async def check_review(
    word_id: int,
    user_meaning: str,
    student_id: int,
    db: AsyncSession,
) -> ReviewResultOut:
    """O'quvchi swipe qilib o'zi yozgan ma'noni AI orqali tekshirish"""
    word_q = select(UserDictionary).where(
        UserDictionary.id == word_id,
        UserDictionary.student_id == student_id,
    )
    word = (await db.execute(word_q)).scalar_one_or_none()
    if not word:
        raise HTTPException(status_code=404, detail="So'z topilmadi")

    correct_meaning = word.context or ""
    if not correct_meaning:
        raise HTTPException(status_code=400, detail="Bu so'zning lug'atda asl ma'nosi saqlanmagan.")

    # AI xizmatini chaqiramiz
    check_result = await check_word_meaning_with_ai(
        word=word.word,
        correct_meaning=correct_meaning,
        user_meaning=user_meaning.strip(),
    )

    is_correct = check_result.get("is_correct", False)
    ai_feedback = check_result.get("feedback", "AI tahlil qila olmadi.")

    # Statistika yangilanadi
    word.review_count += 1
    word.last_reviewed_at = datetime.now(timezone.utc)
    if is_correct:
        word.correct_count += 1
    else:
        word.incorrect_count += 1

    await db.commit()

    return ReviewResultOut(
        word_id=word.id,
        word=word.word,
        is_correct=is_correct,
        correct_meaning=correct_meaning,
        ai_feedback=ai_feedback,
    )