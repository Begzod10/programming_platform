"""Bot-facing Telegram API (shared-secret auth): link a chat by code, list active chats, unlink a chat."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.bot_stats import _require_bot_secret
from app.dependencies import get_db
from app.services import telegram_chats as svc

router = APIRouter()


class LinkBody(BaseModel):
    code: str
    chat_id: int
    chat_title: Optional[str] = None


class UnlinkBody(BaseModel):
    chat_id: int


class StudentBrief(BaseModel):
    id: int
    name: str


class BotChatRead(BaseModel):
    chat_id: int
    title: Optional[str] = None
    students: List[StudentBrief]


@router.post("/telegram/link")
async def link(body: LinkBody, x_internal_secret: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    _require_bot_secret(x_internal_secret)
    try:
        chat, teacher_name = await svc.link_chat(db, body.code, body.chat_id, body.chat_title)
    except svc.LinkCodeInvalid:
        raise HTTPException(status_code=404, detail="Kod yaroqsiz yoki muddati o'tgan")
    except svc.ChatTakenError:
        raise HTTPException(status_code=409, detail="Bu guruh boshqa o'qituvchiga ulangan")
    return {"ok": True, "teacher_name": teacher_name, "chat_row_id": chat.id}


@router.get("/telegram/chats", response_model=List[BotChatRead])
async def chats(x_internal_secret: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    _require_bot_secret(x_internal_secret)
    return await svc.bot_chats(db)


@router.post("/telegram/unlink")
async def unlink(body: UnlinkBody, x_internal_secret: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    _require_bot_secret(x_internal_secret)
    return {"ok": True, "found": await svc.deactivate_chat(db, body.chat_id)}
