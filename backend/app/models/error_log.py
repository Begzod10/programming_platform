from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class AppErrorLog(Base):
    """Every unhandled 500 the app has hit, from any account — see
    app/core/exceptions.py's unhandled_exception_handler, the only writer.
    Gives the two dev/test teacher accounts (see _ALLOWED_USERNAMES in
    app/api/v1/endpoints/teacher/error_log.py) one place to review every
    crash instead of needing SSH + `journalctl` on the server (see the
    2026-09-09 login-outage investigation — this table is what that manual
    process should have been from the start)."""

    __tablename__ = "app_error_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    method: Mapped[str] = mapped_column(String(10))
    path: Mapped[str] = mapped_column(String(500))
    error_type: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    traceback: Mapped[str] = mapped_column(Text)
    # Whoever was authenticated when the request crashed — all three are
    # None for an anonymous request (e.g. the /play guest early-learning
    # routes, or a bad token). Username/role are copied at write time
    # rather than joined at read time so a later account rename/deletion
    # never breaks (or silently reattributes) a historical log entry.
    actor_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    actor_username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    actor_role: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
