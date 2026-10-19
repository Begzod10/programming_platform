"""Tell students how many days are left to submit their team-project task.

One notification per open task (assigned / changes_requested) of a team that is still working, in a project
that is not archived or cancelled. Safe to re-run the same day: a task already reminded today is skipped.
The deadline is soft (a late submission is accepted), the text says so when it has passed.

    python scripts/remind_team_task_deadlines.py            # dry-run: who would get what
    python scripts/remind_team_task_deadlines.py --apply    # create the notifications
"""
from __future__ import annotations
import asyncio, math, sys
from datetime import timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.notification import Notification  # noqa: E402
from app.models.team_project import (  # noqa: E402
    TaskStatus, TeamProject, TeamProjectStatus, TeamProjectTask, TeamProjectTeam, TeamStatus,
)
from app.services.notification_service import _emit  # noqa: E402
from app.utils.datetime_utils import utcnow  # noqa: E402

NOTE_TYPE = "team_task_deadline"


def days_left(deadline, now) -> int:
    """Whole days until the deadline, rounded up (a deadline in 5 hours is '1 day'); negative = overdue."""
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    return math.ceil((deadline - now).total_seconds() / 86400)


def message(title: str, left: int, deadline) -> tuple[str, str]:
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


async def main(apply: bool) -> None:
    now = utcnow()
    today = now.strftime("%Y-%m-%d")
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(
            select(TeamProjectTask, TeamProjectTeam, TeamProject)
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
        done_today = set((await db.execute(
            select(Notification.extra).where(Notification.type == NOTE_TYPE, Notification.extra.like(f"%:{today}"))
        )).scalars().all())
        sent = 0
        for task, team, tp in rows:
            tag = f"t{task.id}:{today}"
            left = days_left(task.deadline_at, now)
            head, body = message(task.title, left, task.deadline_at)
            skip = tag in done_today
            print(f"team {team.id} task #{task.order} student {task.assigned_student_id} left={left:>3} "
                  f"{'(already sent today) ' if skip else ''}| {head}")
            if apply and not skip:
                await _emit(db, task.assigned_student_id, type=NOTE_TYPE, tone="wait", title=head, body=body,
                            extra=tag, icon="⏰", link="/student/team-projects")
                sent += 1
        if apply:
            await db.commit()
        print(f"\n{'sent' if apply else 'DRY-RUN, would send'}: {sent if apply else sum(1 for t, *_ in rows if f't{t.id}:{today}' not in done_today)} of {len(rows)} open tasks")


if __name__ == "__main__":
    asyncio.run(main("--apply" in sys.argv))
