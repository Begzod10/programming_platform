"""Teacher code tasks: scope, the task state machine, points and the AI review.

assigned/returned --submit--> submitted --grade--> graded
                                  \\--return--> returned
The teacher side works on the tasks the teacher created; the student side on the student's own. See
docs/superpowers/specs/2026-11-09-teacher-code-tasks-design.md.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.code_task import (
    ASSIGNED, CODE_TASK_LANGUAGES, MAX_CODE_CHARS, RETURNED, CodeTask, CodeTaskSubmission,
)
from app.services.teacher_students import teacher_student_ids_subquery

logger = logging.getLogger(__name__)

EDITABLE = (ASSIGNED, RETURNED)          # the states in which the teacher may edit and the student may write


class TaskNotFound(Exception):
    """Missing, or not the caller's: both look the same from outside."""


class WrongState(Exception):
    """The task is not in a state that allows this action."""


class InvalidInput(Exception):
    """A value the endpoint's schema cannot catch (e.g. points above this task's maximum)."""


def _aware(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


async def student_in_scope(db: AsyncSession, teacher_id: int, student_id: int) -> bool:
    sub = teacher_student_ids_subquery(teacher_id)
    row = (await db.execute(select(sub.c.student_id).where(sub.c.student_id == student_id))).first()
    return row is not None


async def create_task(db: AsyncSession, teacher_id: int, *, student_id: int, title: str, description: str,
                      language: str, starter_code: Optional[str], max_points: int,
                      deadline: Optional[datetime], review_lang: str) -> CodeTask:
    if language not in CODE_TASK_LANGUAGES:
        raise InvalidInput("language")
    if not await student_in_scope(db, teacher_id, student_id):
        raise TaskNotFound()
    task = CodeTask(teacher_id=teacher_id, student_id=student_id, title=title, description=description,
                    language=language, starter_code=starter_code, max_points=max_points,
                    deadline=_aware(deadline), review_lang=review_lang)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_teacher_task(db: AsyncSession, teacher_id: int, task_id: int, *, for_update: bool = False) -> CodeTask:
    task = await db.get(CodeTask, task_id, with_for_update=for_update, populate_existing=for_update)
    if task is None or task.teacher_id != teacher_id:
        raise TaskNotFound()
    return task


async def update_task(db: AsyncSession, task: CodeTask, **fields) -> CodeTask:
    if task.status not in EDITABLE:
        raise WrongState()
    if "language" in fields and fields["language"] not in CODE_TASK_LANGUAGES:
        raise InvalidInput("language")
    for key in ("title", "description", "language", "starter_code", "max_points"):
        if key in fields:
            setattr(task, key, fields[key])
    if "deadline" in fields:
        task.deadline = _aware(fields["deadline"])
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task: CodeTask) -> None:
    attempts = (await db.execute(
        select(func.count(CodeTaskSubmission.id)).where(CodeTaskSubmission.task_id == task.id))).scalar() or 0
    if task.status != ASSIGNED or attempts:
        raise WrongState()
    await db.delete(task)
    await db.commit()


async def list_for_teacher(db: AsyncSession, teacher_id: int, student_id: int) -> list[CodeTask]:
    if not await student_in_scope(db, teacher_id, student_id):
        raise TaskNotFound()
    return list((await db.execute(
        select(CodeTask).where(CodeTask.teacher_id == teacher_id, CodeTask.student_id == student_id)
        .order_by(CodeTask.id.desc()))).scalars().all())


async def submissions_of(db: AsyncSession, task_id: int) -> list[CodeTaskSubmission]:
    return list((await db.execute(
        select(CodeTaskSubmission).where(CodeTaskSubmission.task_id == task_id)
        .order_by(CodeTaskSubmission.attempt_no))).scalars().all())
