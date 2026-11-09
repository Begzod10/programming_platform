"""Teacher code tasks: scope, the task state machine, points and the AI review.

assigned/returned --submit--> submitted --grade--> graded
                                  \\--return--> returned
The teacher side works on the tasks the teacher created; the student side on the student's own. See
docs/superpowers/specs/2026-11-09-teacher-code-tasks-design.md.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.code_task import (
    ASSIGNED, CODE_TASK_LANGUAGES, GRADED, MAX_CODE_CHARS, RETURNED, SUBMITTED, CodeTask, CodeTaskSubmission,
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


# ── student side ─────────────────────────────────────────────────────────────

async def get_student_task(db: AsyncSession, student_id: int, task_id: int, *, for_update: bool = False) -> CodeTask:
    task = await db.get(CodeTask, task_id, with_for_update=for_update, populate_existing=for_update)
    if task is None or task.student_id != student_id:
        raise TaskNotFound()
    return task


async def list_for_student(db: AsyncSession, student_id: int) -> list[CodeTask]:
    return list((await db.execute(
        select(CodeTask).where(CodeTask.student_id == student_id).order_by(CodeTask.id.desc()))).scalars().all())


async def last_return_feedback(db: AsyncSession, task_id: int) -> Optional[str]:
    return (await db.execute(
        select(CodeTaskSubmission.return_feedback)
        .where(CodeTaskSubmission.task_id == task_id, CodeTaskSubmission.return_feedback.is_not(None))
        .order_by(CodeTaskSubmission.attempt_no.desc()).limit(1))).scalar_one_or_none()


def _check_length(code: str) -> None:
    if len(code) > MAX_CODE_CHARS:
        raise InvalidInput("code too long")


async def save_draft(db: AsyncSession, task: CodeTask, code: str) -> CodeTask:
    """Autosave. An empty draft is allowed (the student cleared the editor); only submitting needs real code."""
    if task.status not in EDITABLE:
        raise WrongState()
    _check_length(code)
    task.draft_code = code
    task.draft_saved_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(task)
    return task


async def submit(db: AsyncSession, task: CodeTask, *, code: str, active_seconds: int, typed_chars: int,
                 pasted_chars: int, paste_events: int, started_at: Optional[datetime]) -> CodeTaskSubmission:
    """assigned/returned -> submitted, one attempt row. The status flip is a conditional UPDATE, so two
    simultaneous submits cannot both pass (SQLite has no row locks; the unique attempt number is the second guard)."""
    if task.status not in EDITABLE:
        raise WrongState()
    if not code.strip():
        raise InvalidInput("empty code")
    _check_length(code)
    flipped = await db.execute(
        update(CodeTask).where(CodeTask.id == task.id, CodeTask.status.in_(EDITABLE))
        .values(status=SUBMITTED, draft_code=None, draft_saved_at=None))
    if flipped.rowcount != 1:
        await db.rollback()
        raise WrongState()
    attempts = (await db.execute(
        select(func.count(CodeTaskSubmission.id)).where(CodeTaskSubmission.task_id == task.id))).scalar() or 0
    sub = CodeTaskSubmission(
        task_id=task.id, attempt_no=attempts + 1, code=code, started_at=_aware(started_at),
        active_seconds=active_seconds, typed_chars=typed_chars, pasted_chars=pasted_chars, paste_events=paste_events)
    db.add(sub)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise WrongState()
    await db.refresh(sub)
    return sub


# ── the teacher's verdict ────────────────────────────────────────────────────

async def grade(db: AsyncSession, task: CodeTask, *, points: int, feedback: Optional[str]) -> CodeTask:
    """submitted -> graded, once. The points go to the student through the platform's single award point in the
    same transaction as the status flip, and the flip is a conditional UPDATE, so a double click or two tabs
    can never award twice."""
    if task.status != SUBMITTED:
        raise WrongState()
    if not 0 <= points <= task.max_points:
        raise InvalidInput("points")
    flipped = await db.execute(
        update(CodeTask).where(CodeTask.id == task.id, CodeTask.status == SUBMITTED)
        .values(status=GRADED, graded_points=points, teacher_feedback=(feedback or "").strip() or None,
                graded_at=datetime.now(timezone.utc)))
    if flipped.rowcount != 1:
        await db.rollback()
        raise WrongState()
    if points > 0:
        from app.services.ranking_service import RankingService
        await RankingService(db).add_points_to_student(task.student_id, points)    # commits
    else:
        await db.commit()
    await db.refresh(task)
    return task


async def return_task(db: AsyncSession, task: CodeTask, *, feedback: str) -> CodeTask:
    """submitted -> returned: the teacher asks for another attempt and says why."""
    if task.status != SUBMITTED:
        raise WrongState()
    note = (feedback or "").strip()
    if not note:
        raise InvalidInput("feedback")
    flipped = await db.execute(
        update(CodeTask).where(CodeTask.id == task.id, CodeTask.status == SUBMITTED).values(status=RETURNED))
    if flipped.rowcount != 1:
        await db.rollback()
        raise WrongState()
    latest = (await db.execute(
        select(CodeTaskSubmission).where(CodeTaskSubmission.task_id == task.id)
        .order_by(CodeTaskSubmission.attempt_no.desc()).limit(1))).scalar_one_or_none()
    if latest is not None:
        latest.return_feedback = note
        latest.returned_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(task)
    return task


async def run_ai_review(submission_id: int) -> None:
    """Replaced by the real AI review in the next step; kept as a no-op so submit can already schedule it."""
    return None
