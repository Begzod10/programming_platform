from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.db.session import get_db
from app.models import Lesson
from app.models.dictionary import UserDictionary
from app.models.user import Student
from app.dependencies import get_current_student
from pydantic import BaseModel
from typing import Optional

from app.services.grok_service import explain_word_with_ai

router = APIRouter()


class DictionaryCreate(BaseModel):
    word: str
    context: Optional[str] = None
    lesson_id: Optional[int] = None


class DictionaryOut(BaseModel):
    id: int
    word: str
    context: Optional[str]
    lesson_id: Optional[int]

    class Config:
        from_attributes = True


@router.post("/", response_model=DictionaryOut)
async def add_word(
        data: DictionaryCreate,
        db: AsyncSession = Depends(get_db),
        current_user: Student = Depends(get_current_student)
):
    # lesson_id mavjudligini tekshirish
    if data.lesson_id:
        lesson = await db.execute(select(Lesson).where(Lesson.id == data.lesson_id))
        if not lesson.scalar_one_or_none():
            data.lesson_id = None  # mavjud bo'lmasa NULL qilib saqlash

    word = UserDictionary(
        student_id=current_user.id,
        word=data.word,
        context=data.context,
        lesson_id=data.lesson_id
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
async def explain_word(data: DictionaryCreate):
    result = await explain_word_with_ai(data.word)
    return result
