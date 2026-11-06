"""A teacher's Telegram group and which of the teacher's students it reports on.

The platform owns this data; the parent bot only asks for it (GET /bot/telegram/chats) and reports link
events (POST /bot/telegram/link, /unlink). See docs/superpowers/specs/2026-11-06-telegram-teacher-chats-design.md.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.utils.datetime_utils import utcnow


class TelegramChat(Base):
    """One Telegram group linked to one teacher (chat_id is unique: a chat has a single owner)."""
    __tablename__ = "telegram_chats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    # False once the bot was removed from the chat; the row stays so the teacher sees why reports stopped.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_error: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class TelegramChatStudent(Base):
    """A student the teacher chose for a chat. Whether the student is still reportable (in the teacher's
    classes, active, not demo) is decided when the report is built, never stored."""
    __tablename__ = "telegram_chat_students"

    chat_row_id: Mapped[int] = mapped_column(
        ForeignKey("telegram_chats.id", ondelete="CASCADE"), primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)


class TelegramLinkCode(Base):
    """One-time code carried by the t.me/<bot>?startgroup=<code> link: proves which teacher adds the bot."""
    __tablename__ = "telegram_link_codes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
