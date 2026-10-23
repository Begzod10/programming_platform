"""Reminders: how many days are left to submit a team-project task.

One notification per open task (assigned / changes_requested) of a team that is still working, in a project that
is not archived or cancelled. The deadline is soft (a late submission is accepted), so overdue text says so.
`send_deadline_reminders` is idempotent per task per day. The scheduler (app/scheduler.py) runs it every morning with
`milestones_only=True`; scripts/remind_team_task_deadlines.py can send to everyone on demand.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.team_project import (
    TaskStatus, TeamProject, TeamProjectStatus, TeamProjectTask, TeamProjectTeam, TeamStatus,
)
from app.utils.datetime_utils import utcnow

logger = logging.getLogger(__name__)

LOCAL_TZ = ZoneInfo("Asia/Tashkent")
NOTE_TYPE = "team_task_deadline"
# Days left on which the daily run speaks up: a week, 3 days, tomorrow, today, then once overdue and again 3 days later.
MILESTONES = (7, 3, 1, 0, -1, -3)


def days_left(deadline: datetime, now: datetime) -> int:
    """Calendar days from today to the deadline's day in Tashkent time: 0 = the deadline is today, 1 = tomorrow,
    -1 = it was yesterday. (Rounding hours instead said "deadline today" the morning after a 23:59 deadline.)"""
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return (deadline.astimezone(LOCAL_TZ).date() - now.astimezone(LOCAL_TZ).date()).days


def message(title: str, left: int, deadline: datetime) -> tuple[str, str]:
    date = deadline.strftime("%d.%m.%Y")
    if left < 0:
        head = f"Jamoaviy loyiha: muddat {-left} kun oldin o'tdi"
        body = (f"«{title}» vazifasi topshirilmagan (muddat: {date}). Hali ham topshirishingiz mumkin, "
                f"jamoangiz sizni kutyapti.\n\nПроект команды: срок прошёл {-left} дн. назад. Задача «{title}» "
                "не сдана — её всё ещё можно сдать, команда вас ждёт.")
    elif left == 0:
        head = "Jamoaviy loyiha: muddat bugun!"
        body = (f"«{title}» vazifasini bugun topshiring (muddat: {date}).\n\n"
                f"Проект команды: срок сегодня! Сдайте задачу «{title}».")
    else:
        head = f"Jamoaviy loyiha: topshirishga {left} kun qoldi"
        body = (f"«{title}» vazifasini topshirish uchun {left} kun bor (muddat: {date}).\n\n"
                f"Проект команды: до сдачи задачи «{title}» осталось {left} дн. (срок: {date}).")
    return head, body


async def open_tasks(db: AsyncSession):
    return (await db.execute(
        select(TeamProjectTask, TeamProjectTeam)
        .join(TeamProjectTeam, TeamProjectTeam.id == TeamProjectTask.team_id)
        .join(TeamProject, TeamProject.id == TeamProjectTeam.team_project_id)
        .where(
            TeamProjectTask.status.in_([TaskStatus.assigned, TaskStatus.changes_requested]),
            TeamProjectTask.deadline_at.is_not(None),
            TeamProjectTask.assigned_student_id.is_not(None),
            TeamProjectTeam.status == TeamStatus.working,
            TeamProject.archived_at.is_(None),
            TeamProject.status.not_in([TeamProjectStatus.reviewed, TeamProjectStatus.cancelled]),
        ).order_by(TeamProjectTeam.id, TeamProjectTask.order)
    )).all()


async def send_deadline_reminders(db: AsyncSession, *, apply: bool = True, milestones_only: bool = True,
                                  now: Optional[datetime] = None) -> list[dict]:
    """Returns what was (or, with apply=False, would be) sent: [{task_id, team_id, student_id, left, title, skipped}]."""
    from app.services.notification_service import _emit
    now = now or utcnow()
    today = now.strftime("%Y-%m-%d")
    done_today = set((await db.execute(
        select(Notification.extra).where(Notification.type == NOTE_TYPE, Notification.extra.like(f"%:{today}"))
    )).scalars().all())
    out = []
    for task, team in await open_tasks(db):
        left = days_left(task.deadline_at, now)
        if milestones_only and left not in MILESTONES:
            continue
        tag = f"t{task.id}:{today}"
        skipped = tag in done_today
        head, body = message(task.title, left, task.deadline_at)
        out.append({"task_id": task.id, "team_id": team.id, "student_id": task.assigned_student_id,
                    "left": left, "title": head, "skipped": skipped})
        if apply and not skipped:
            await _emit(db, task.assigned_student_id, type=NOTE_TYPE, tone="wait", title=head, body=body,
                        extra=tag, icon="⏰", link="/student/team-projects")
    if apply:
        await db.commit()
    return out
