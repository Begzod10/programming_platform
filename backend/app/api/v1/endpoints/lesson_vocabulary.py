"""Lesson vocabulary endpoints (teacher manages, students check and save words)."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_student, get_current_instructor
from app.models.dictionary import UserDictionary
from app.models.course import Course
from app.models.lesson import Lesson, LessonVocabulary
from app.models.user import Student
from app.services import lesson_vocab_ai_service
from app.services.grok_ai_client import ProviderError

router = APIRouter()


class VocabIn(BaseModel):
    word: str
    definition: str
    definition_ru: Optional[str] = None
    order: int = 0


class VocabOut(BaseModel):
    id: int
    word: str
    definition: str
    definition_ru: Optional[str] = None
    source: str = "manual"
    order: int

    class Config:
        from_attributes = True


@router.get("/courses/{course_id}/lessons/{lesson_id}/vocabulary", response_model=List[VocabOut])
async def get_lesson_vocabulary(
        lesson_id: int,
        course_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_student),
):
    rows = (await db.execute(
        select(LessonVocabulary)
        .where(LessonVocabulary.lesson_id == lesson_id)
        .order_by(LessonVocabulary.order, LessonVocabulary.id)
    )).scalars().all()
    return rows


@router.post("/courses/{course_id}/lessons/{lesson_id}/vocabulary", response_model=VocabOut)
async def add_vocab_word(
        lesson_id: int,
        course_id: int,
        data: VocabIn,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_instructor),
):
    word = data.word.strip()
    definition = data.definition.strip()
    if not word or not definition:
        raise HTTPException(status_code=422, detail="So'z va ta'rif bo'sh bo'lishi mumkin emas")
    vocab = LessonVocabulary(lesson_id=lesson_id, word=word, definition=definition,
                             definition_ru=(data.definition_ru or "").strip() or None, order=data.order)
    db.add(vocab)
    await db.commit()
    await db.refresh(vocab)
    return vocab


@router.post("/courses/{course_id}/lessons/{lesson_id}/vocabulary/generate")
async def generate_vocabulary(
        lesson_id: int,
        course_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_instructor),
):
    """AI adds the lesson's key terms (UZ + RU). Only the course owner; words already there are left alone."""
    course = await db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Kurs topilmadi")
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bu kurs sizga tegishli emas")
    lesson = await db.get(Lesson, lesson_id)
    if lesson is None or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="Dars topilmadi")
    try:
        added = await lesson_vocab_ai_service.generate_for_lesson(db, lesson_id)
    except ProviderError:
        raise HTTPException(status_code=502, detail="AI hozircha ishlamayapti, keyinroq urinib ko'ring")
    return {"added": added}


@router.put("/courses/{course_id}/lessons/{lesson_id}/vocabulary/{vocab_id}", response_model=VocabOut)
async def update_vocab_word(
        lesson_id: int,
        course_id: int,
        vocab_id: int,
        data: VocabIn,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_instructor),
):
    vocab = (await db.execute(
        select(LessonVocabulary).where(
            LessonVocabulary.id == vocab_id,
            LessonVocabulary.lesson_id == lesson_id,
        )
    )).scalar_one_or_none()
    if not vocab:
        raise HTTPException(status_code=404, detail="Topilmadi")
    vocab.word = data.word.strip()
    vocab.definition = data.definition.strip()
    if data.definition_ru is not None:  # omitted = keep the Russian definition as it is
        vocab.definition_ru = data.definition_ru.strip() or None
    vocab.order = data.order
    await db.commit()
    await db.refresh(vocab)
    return vocab


@router.delete("/courses/{course_id}/lessons/{lesson_id}/vocabulary/{vocab_id}")
async def delete_vocab_word(
        lesson_id: int,
        course_id: int,
        vocab_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_instructor),
):
    vocab = (await db.execute(
        select(LessonVocabulary).where(
            LessonVocabulary.id == vocab_id,
            LessonVocabulary.lesson_id == lesson_id,
        )
    )).scalar_one_or_none()
    if not vocab:
        raise HTTPException(status_code=404, detail="Topilmadi")
    await db.delete(vocab)
    await db.commit()
    return {"ok": True}


@router.post("/courses/{course_id}/lessons/{lesson_id}/vocabulary/{vocab_id}/add-to-dict")
async def add_vocab_to_dict(
        lesson_id: int,
        course_id: int,
        vocab_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_student),
):
    """Student marks a vocab word as unknown — add it to their personal dictionary."""
    vocab = (await db.execute(
        select(LessonVocabulary).where(LessonVocabulary.id == vocab_id)
    )).scalar_one_or_none()
    if not vocab:
        raise HTTPException(status_code=404, detail="Topilmadi")

    existing = (await db.execute(
        select(UserDictionary).where(
            UserDictionary.student_id == current_user.id,
            func.lower(UserDictionary.word) == vocab.word.lower(),
        )
    )).scalar_one_or_none()
    if existing:
        return {"ok": True, "already_exists": True}

    db.add(UserDictionary(
        student_id=current_user.id,
        word=vocab.word,
        context=vocab.definition,
        lesson_id=lesson_id,
    ))
    await db.commit()
    return {"ok": True, "already_exists": False}
