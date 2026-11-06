"""Teacher-side management of Telegram groups: add a group (link code), pick students, disconnect."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_db, get_current_instructor
from app.models.telegram_chat import TelegramChat, TelegramChatStudent
from app.models.user import Student
from app.services import telegram_chats as svc

router = APIRouter()


class LinkCodeRead(BaseModel):
    code: str
    url: str
    expires_at: datetime


class StudentBrief(BaseModel):
    id: int
    name: str


class ChatRead(BaseModel):
    id: int
    title: Optional[str] = None
    is_active: bool
    linked_at: datetime
    last_error: Optional[str] = None
    students: List[StudentBrief]


class TeacherStudentRead(BaseModel):
    id: int
    name: str
    classes: List[str]


class SelectionBody(BaseModel):
    student_ids: List[int]


class SelectionRead(BaseModel):
    students: List[StudentBrief]


async def _own_chat(db: AsyncSession, chat_id: int, teacher: Student) -> TelegramChat:
    chat = (await db.execute(select(TelegramChat).where(
        TelegramChat.id == chat_id, TelegramChat.teacher_id == teacher.id))).scalar_one_or_none()
    if chat is None:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")
    return chat


@router.post("/link-code", response_model=LinkCodeRead)
async def create_link_code(teacher: Student = Depends(get_current_instructor), db: AsyncSession = Depends(get_db)):
    row = await svc.create_link_code(db, teacher.id)
    return LinkCodeRead(
        code=row.code, expires_at=row.expires_at,
        url=f"https://t.me/{settings.PARENT_BOT_USERNAME}?startgroup={row.code}",
    )


@router.get("/chats", response_model=List[ChatRead])
async def list_chats(teacher: Student = Depends(get_current_instructor), db: AsyncSession = Depends(get_db)):
    chats = (await db.execute(select(TelegramChat).where(TelegramChat.teacher_id == teacher.id)
                              .order_by(TelegramChat.linked_at.desc()))).scalars().all()
    return [
        ChatRead(id=c.id, title=c.title, is_active=c.is_active, linked_at=c.linked_at, last_error=c.last_error,
                 students=await svc.chat_students(db, c.id))
        for c in chats
    ]


@router.get("/students", response_model=List[TeacherStudentRead])
async def my_students(search: Optional[str] = Query(None),
                      teacher: Student = Depends(get_current_instructor), db: AsyncSession = Depends(get_db)):
    return await svc.list_teacher_students(db, teacher.id, search)


@router.put("/chats/{chat_id}/students", response_model=SelectionRead)
async def set_students(chat_id: int, body: SelectionBody,
                       teacher: Student = Depends(get_current_instructor), db: AsyncSession = Depends(get_db)):
    chat = await _own_chat(db, chat_id, teacher)
    try:
        await svc.set_chat_students(db, chat, body.student_ids, teacher.id)
    except svc.ForeignStudentError:
        raise HTTPException(status_code=403, detail="Bu o'quvchi sizning o'quvchingiz emas")
    return SelectionRead(students=await svc.chat_students(db, chat.id))


@router.delete("/chats/{chat_id}", status_code=204)
async def disconnect(chat_id: int, teacher: Student = Depends(get_current_instructor),
                     db: AsyncSession = Depends(get_db)):
    chat = await _own_chat(db, chat_id, teacher)
    # explicit: do not rely on the FK cascade (SQLite test DB has none)
    await db.execute(delete(TelegramChatStudent).where(TelegramChatStudent.chat_row_id == chat.id))
    await db.delete(chat)
    await db.commit()
    return Response(status_code=204)
