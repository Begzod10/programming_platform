"""Submission rules and the 20-minute ban for breaking them.

The teacher can't read every submission, so rule-breaking is handled here,
BEFORE the AI grader runs: the project is rejected with the reason, a
ProjectViolation row is written, and the student can't submit anything for
BAN_DURATION. The ban is derived from the newest violation row — there is no
"banned until" column to drift out of sync.

Deliberately NOT violations (plain rejection / no penalty): code saved as
.txt (a mistake, caught at upload with a hint), empty or template-only work,
and speed on its own — a strong student submitting several correct projects
quickly isn't breaking a rule, and anything actually copied is caught by the
content checks below.
"""
from __future__ import annotations

from datetime import timedelta, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, ProjectViolation
from app.utils.datetime_utils import utcnow

BAN_DURATION = timedelta(minutes=20)

# Rejections in a row that count as spamming the grader. Rejected projects
# skip the normal 10-minute cooldown (so a student can fix and retry at
# once); this is what stops that from becoming a free retry loop.
REPEATED_REJECTIONS_LIMIT = 3
REPEATED_REJECTIONS_WINDOW = timedelta(minutes=20)

# code -> (uzbek, russian) reason shown to the student
REASONS: dict[str, tuple[str, str]] = {
    "duplicate_content": (
        "kodingiz boshqa o'quvchining ishi bilan bir xil",
        "ваш код совпадает с работой другого ученика",
    ),
    "sample_copy": (
        "darsning namuna (sample) kodini ko'chirgansiz",
        "вы скопировали пример кода из урока",
    ),
    "prompt_injection": (
        "kod ichida AI baholovchiga ball haqida ko'rsatma yozilgan",
        "в коде есть инструкция для AI-проверяющего о баллах",
    ),
    "unchanged_resubmission": (
        "rad etilgan kodni o'zgartirmasdan qayta yubordingiz",
        "вы повторно отправили отклонённый код без изменений",
    ),
    "repeated_rejections": (
        f"{REPEATED_REJECTIONS_WINDOW.seconds // 60} daqiqada {REPEATED_REJECTIONS_LIMIT} ta loyiha rad etildi",
        f"за {REPEATED_REJECTIONS_WINDOW.seconds // 60} минут отклонено {REPEATED_REJECTIONS_LIMIT} проекта",
    ),
}


def reason_text(code: str) -> tuple[str, str]:
    return REASONS.get(code, ("qoidabuzarlik", "нарушение правил"))


def ban_notice(code: str) -> str:
    uz, ru = reason_text(code)
    minutes = int(BAN_DURATION.total_seconds() // 60)
    return (
        f"⛔ Qoida buzildi: {uz}. {minutes} daqiqa davomida yangi loyiha topshira olmaysiz.\n"
        f"⛔ Правило нарушено: {ru}. {minutes} минут вы не сможете отправлять новые проекты."
    )


async def record_violation(
        db: AsyncSession, *, student_id: int, project_id: Optional[int], code: str,
        detail: Optional[str] = None,
) -> ProjectViolation:
    row = ProjectViolation(student_id=student_id, project_id=project_id, code=code, detail=detail)
    db.add(row)
    await db.flush()
    return row


async def active_ban(db: AsyncSession, student_id: int) -> Optional[tuple[int, str]]:
    """(seconds_left, code) if the student is currently banned, else None."""
    row = (await db.execute(
        select(ProjectViolation.created_at, ProjectViolation.code)
        .where(ProjectViolation.student_id == student_id)
        .order_by(ProjectViolation.created_at.desc())
        .limit(1)
    )).first()
    if row is None:
        return None
    started, code = row
    if started.tzinfo is None:  # SQLite hands back naive datetimes
        started = started.replace(tzinfo=timezone.utc)
    left = (started + BAN_DURATION - utcnow()).total_seconds()
    if left <= 0:
        return None
    return int(left + 0.999), code


async def recent_rejections(db: AsyncSession, student_id: int) -> int:
    """Rejected projects of this student submitted within the window."""
    since = utcnow() - REPEATED_REJECTIONS_WINDOW
    return (await db.execute(
        select(func.count(Project.id)).where(
            Project.student_id == student_id,
            Project.status == "Rejected",
            Project.submitted_at.is_not(None),
            Project.submitted_at >= since,
        )
    )).scalar_one()
