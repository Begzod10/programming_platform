"""Teacher's Telegram chats: link codes, student selection, what a chat's report covers.

Every student id that can reach a chat goes through the teacher's own scope (teacher_student_ids_subquery);
that check lives here, in one place, for both the teacher API and the bot API.
"""
import secrets
from datetime import timedelta
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.flow import Flow, student_flows
from app.models.group import Group, student_groups
from app.models.telegram_chat import TelegramChat, TelegramChatStudent, TelegramLinkCode
from app.models.user import Student, UserRole
from app.services.teacher_students import teacher_student_ids_subquery
from app.utils.datetime_utils import utcnow

LINK_CODE_TTL = timedelta(hours=1)


class ForeignStudentError(Exception):
    """A student id outside the teacher's own students."""


def _scope(teacher_id: int):
    return select(teacher_student_ids_subquery(teacher_id).c.student_id)


def _name(full_name: Optional[str], username: str) -> str:
    return full_name or username


async def create_link_code(db: AsyncSession, teacher_id: int) -> TelegramLinkCode:
    row = TelegramLinkCode(code=secrets.token_urlsafe(18), teacher_id=teacher_id,
                           expires_at=utcnow() + LINK_CODE_TTL)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def list_teacher_students(db: AsyncSession, teacher_id: int, search: Optional[str] = None) -> list[dict]:
    """The teacher's reportable students (active, not demo) with the names of the teacher's own classes."""
    q = (
        select(Student).where(
            Student.id.in_(_scope(teacher_id)),
            Student.role == UserRole.student, Student.is_active.is_(True), Student.is_demo.is_(False),
        ).order_by(Student.full_name, Student.username)
    )
    if search and search.strip():
        like = f"%{search.strip()}%"
        q = q.where(Student.full_name.ilike(like) | Student.username.ilike(like))
    students = (await db.execute(q)).scalars().all()
    if not students:
        return []
    ids = [s.id for s in students]

    classes: dict[int, set[str]] = {i: set() for i in ids}
    for sid, name in (await db.execute(
        select(student_groups.c.student_id, Group.name)
        .join(Group, Group.id == student_groups.c.group_id)
        .where(Group.teacher_id == teacher_id, student_groups.c.student_id.in_(ids))
    )).all():
        classes[sid].add(name)
    for sid, name in (await db.execute(
        select(student_flows.c.student_id, Flow.name)
        .join(Flow, Flow.id == student_flows.c.flow_id)
        .where(Flow.teacher_id == teacher_id, student_flows.c.student_id.in_(ids))
    )).all():
        classes[sid].add(name)
    return [{"id": s.id, "name": _name(s.full_name, s.username), "classes": sorted(classes[s.id])}
            for s in students]


async def set_chat_students(db: AsyncSession, chat: TelegramChat, student_ids: list[int], teacher_id: int) -> None:
    """Replace the chat's selection. Any id outside the teacher's scope aborts the whole call, nothing saved."""
    wanted = set(student_ids)
    if wanted:
        in_scope = set((await db.execute(
            select(Student.id).where(Student.id.in_(wanted), Student.id.in_(_scope(teacher_id)))
        )).scalars().all())
        if in_scope != wanted:
            raise ForeignStudentError()
    await db.execute(delete(TelegramChatStudent).where(TelegramChatStudent.chat_row_id == chat.id))
    for sid in sorted(wanted):
        db.add(TelegramChatStudent(chat_row_id=chat.id, student_id=sid))
    await db.commit()


async def chat_students(db: AsyncSession, chat_row_id: int) -> list[dict]:
    """The students a chat reports on right now: selection ∩ the owner's scope, active, not demo."""
    chat = (await db.execute(select(TelegramChat).where(TelegramChat.id == chat_row_id))).scalar_one_or_none()
    if chat is None:
        return []
    rows = (await db.execute(
        select(Student).join(TelegramChatStudent, TelegramChatStudent.student_id == Student.id)
        .where(
            TelegramChatStudent.chat_row_id == chat_row_id,
            Student.id.in_(_scope(chat.teacher_id)),
            Student.role == UserRole.student, Student.is_active.is_(True), Student.is_demo.is_(False),
        ).order_by(Student.full_name, Student.username)
    )).scalars().all()
    return [{"id": s.id, "name": _name(s.full_name, s.username)} for s in rows]


class LinkCodeInvalid(Exception):
    """Unknown, already used or expired link code."""


class ChatTakenError(Exception):
    """The chat is already linked (and active) under another teacher."""


def _aware(dt):
    from datetime import timezone
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)   # SQLite returns naive datetimes


async def link_chat(db: AsyncSession, code: str, chat_id: int, title: Optional[str]) -> tuple[TelegramChat, str]:
    """Attach `chat_id` to the teacher who owns `code` and burn the code. Returns (chat, teacher name).

    A chat that is active under another teacher is refused WITHOUT burning the code. A chat the bot was removed
    from (is_active False) is reactivated; if its owner changes the old selection is dropped."""
    row = (await db.execute(
        select(TelegramLinkCode).where(TelegramLinkCode.code == code).with_for_update()
    )).scalar_one_or_none()
    now = utcnow()
    if row is None or row.used_at is not None or _aware(row.expires_at) <= now:
        raise LinkCodeInvalid()

    chat = (await db.execute(
        select(TelegramChat).where(TelegramChat.chat_id == chat_id).with_for_update()
    )).scalar_one_or_none()
    if chat is not None and chat.is_active and chat.teacher_id != row.teacher_id:
        raise ChatTakenError()

    if chat is None:
        chat = TelegramChat(chat_id=chat_id, title=title, teacher_id=row.teacher_id, is_active=True)
        db.add(chat)
        await db.flush()
    else:
        if chat.teacher_id != row.teacher_id:
            await db.execute(delete(TelegramChatStudent).where(TelegramChatStudent.chat_row_id == chat.id))
        chat.teacher_id = row.teacher_id
        chat.is_active = True
        chat.title = title or chat.title
        chat.last_error = None
        chat.linked_at = now
    row.used_at = now
    teacher = (await db.execute(select(Student).where(Student.id == row.teacher_id))).scalar_one()
    teacher_name = _name(teacher.full_name, teacher.username)
    await db.commit()
    await db.refresh(chat)
    return chat, teacher_name


async def bot_chats(db: AsyncSession) -> list[dict]:
    """Active chats with the students each one reports on, for the bot's daily report."""
    chats = (await db.execute(
        select(TelegramChat).where(TelegramChat.is_active.is_(True)).order_by(TelegramChat.id)
    )).scalars().all()
    return [{"chat_id": c.chat_id, "title": c.title, "students": await chat_students(db, c.id)} for c in chats]


async def deactivate_chat(db: AsyncSession, chat_id: int) -> bool:
    """The bot was removed from the chat: keep the row (the teacher sees why reports stopped), stop reporting."""
    chat = (await db.execute(select(TelegramChat).where(TelegramChat.chat_id == chat_id))).scalar_one_or_none()
    if chat is None:
        return False
    chat.is_active = False
    await db.commit()
    return True
