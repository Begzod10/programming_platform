"""10-minute cooldown between a student's project submissions.

After a student submits a project (lesson or standalone), they can't submit
another one for SUBMIT_COOLDOWN. Enforced at every student-facing
submission endpoint (create / submit / upload-zip / lesson submit); team
projects are not affected.

No timer column is stored: the student's most recent Project.submitted_at
already is the timer, so it can never drift out of sync with reality.
`exclude_project_id` lets the project being submitted right now (e.g. a ZIP
upload retry, or /submit right after create) through its own cooldown.

Exception: if that most recent submission was rejected (status=="Rejected"),
the cooldown is skipped so a student who failed can immediately fix and
resubmit instead of waiting out the anti-spam timer meant for students
blasting through fresh submissions. A rejected project has already gone
through review and cost nothing further to retry.
"""
from __future__ import annotations

from datetime import timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.utils.datetime_utils import utcnow

SUBMIT_COOLDOWN = timedelta(minutes=10)


async def seconds_until_can_submit(
        db: AsyncSession,
        student_id: int,
        *,
        exclude_project_id: Optional[int] = None,
) -> int:
    query = select(Project.submitted_at, Project.status).where(
        Project.student_id == student_id,
        Project.submitted_at.is_not(None),
    )
    if exclude_project_id is not None:
        query = query.where(Project.id != exclude_project_id)
    query = query.order_by(Project.submitted_at.desc()).limit(1)
    row = (await db.execute(query)).first()
    if row is None:
        return 0
    last, last_status = row
    if last_status == "Rejected":
        return 0
    if last.tzinfo is None:  # SQLite hands back naive datetimes
        last = last.replace(tzinfo=timezone.utc)
    remaining = (last + SUBMIT_COOLDOWN - utcnow()).total_seconds()
    return max(0, int(remaining + 0.999))


async def enforce_submission_cooldown(
        db: AsyncSession,
        student_id: int,
        *,
        exclude_project_id: Optional[int] = None,
) -> None:
    wait = await seconds_until_can_submit(
        db, student_id, exclude_project_id=exclude_project_id)
    if wait > 0:
        minutes, seconds = divmod(wait, 60)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(f"Keyingi loyihani {minutes} daqiqa {seconds} soniyadan keyin "
                    f"topshirishingiz mumkin (har loyihadan keyin 10 daqiqa kutish)."),
            headers={"Retry-After": str(wait)},
        )
