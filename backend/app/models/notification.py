from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base


class Notification(Base):
    """Per-student notification feed.

    Rows are written at the moment an event happens (a project is reviewed, an
    achievement or certificate is earned) by app.services.notification_service.
    The frontend renders the human-facing heading from ``type`` so the feed
    stays bilingual (uz/ru) — only entity-specific text (project/course name,
    instructor feedback) is stored here; the template words are localized on
    the client.
    """
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Drives icon + localized heading on the frontend, e.g.
    # project_approved / project_rejected / project_submitted / achievement / certificate
    type: Mapped[str] = mapped_column(String(40), nullable=False)
    # Visual accent: ok / bad / wait / star / cert
    tone: Mapped[str] = mapped_column(String(12), nullable=False, default="ok")

    # Entity name (project title, course title, achievement name) — as-is.
    title: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    # Extra detail (instructor feedback, achievement description) — optional.
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Small misc field (e.g. a project grade letter) — optional.
    extra: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)

    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    link: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)

    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_notifications_student_created", "student_id", "created_at"),
        Index("ix_notifications_student_unread", "student_id", "is_read"),
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, student={self.student_id}, type={self.type}, read={self.is_read})>"
