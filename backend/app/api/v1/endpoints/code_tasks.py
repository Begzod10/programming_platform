"""Student side of code tasks. These response models carry NO AI review and NO integrity numbers."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_student, get_db
from app.models.code_task import MAX_CODE_CHARS, CodeTask
from app.models.user import Student
from app.services import code_task_service as svc

router = APIRouter()


class TaskBrief(BaseModel):
    id: int
    title: str
    language: str
    status: str
    max_points: int
    deadline: Optional[datetime] = None
    graded_points: Optional[int] = None


class TaskRead(TaskBrief):
    description: str
    starter_code: Optional[str] = None
    code: str                                   # what the editor opens with: the draft, else the starter code
    draft_saved_at: Optional[datetime] = None
    teacher_feedback: Optional[str] = None
    graded_at: Optional[datetime] = None
    returned_feedback: Optional[str] = None     # the teacher's note when the last attempt was sent back


class DraftBody(BaseModel):
    code: str = Field(max_length=MAX_CODE_CHARS)


class SubmitBody(BaseModel):
    code: str = Field(max_length=MAX_CODE_CHARS)
    active_seconds: int = Field(default=0, ge=0)
    typed_chars: int = Field(default=0, ge=0)
    pasted_chars: int = Field(default=0, ge=0)
    paste_events: int = Field(default=0, ge=0)
    started_at: Optional[datetime] = None


async def _read(db: AsyncSession, task: CodeTask) -> TaskRead:
    return TaskRead(
        id=task.id, title=task.title, language=task.language, status=task.status, max_points=task.max_points,
        deadline=task.deadline, graded_points=task.graded_points, description=task.description,
        starter_code=task.starter_code,
        code=task.draft_code if task.draft_code is not None else (task.starter_code or ""),
        draft_saved_at=task.draft_saved_at, teacher_feedback=task.teacher_feedback, graded_at=task.graded_at,
        returned_feedback=await svc.last_return_feedback(db, task.id))


def _http(exc: Exception) -> HTTPException:
    if isinstance(exc, svc.TaskNotFound):
        return HTTPException(status_code=404, detail="Vazifa topilmadi")
    if isinstance(exc, svc.WrongState):
        return HTTPException(status_code=409, detail="Vazifa hozirgi holatda bu amalni qabul qilmaydi")
    return HTTPException(status_code=422, detail="Kod bo'sh yoki juda uzun")


@router.get("/", response_model=List[TaskBrief])
async def my_tasks(student: Student = Depends(get_current_student), db: AsyncSession = Depends(get_db)):
    return await svc.list_for_student(db, student.id)


@router.get("/{task_id}", response_model=TaskRead)
async def my_task(task_id: int, student: Student = Depends(get_current_student), db: AsyncSession = Depends(get_db)):
    try:
        return await _read(db, await svc.get_student_task(db, student.id, task_id))
    except svc.TaskNotFound as e:
        raise _http(e)


@router.put("/{task_id}/draft", response_model=TaskRead)
async def save_draft(task_id: int, body: DraftBody, student: Student = Depends(get_current_student),
                     db: AsyncSession = Depends(get_db)):
    try:
        task = await svc.get_student_task(db, student.id, task_id, for_update=True)
        return await _read(db, await svc.save_draft(db, task, body.code))
    except (svc.TaskNotFound, svc.WrongState, svc.InvalidInput) as e:
        raise _http(e)


@router.post("/{task_id}/submit", response_model=TaskRead)
async def submit(task_id: int, body: SubmitBody, background: BackgroundTasks,
                 student: Student = Depends(get_current_student), db: AsyncSession = Depends(get_db)):
    try:
        task = await svc.get_student_task(db, student.id, task_id, for_update=True)
        sub = await svc.submit(db, task, **body.model_dump())
    except (svc.TaskNotFound, svc.WrongState, svc.InvalidInput) as e:
        raise _http(e)
    background.add_task(svc.run_ai_review, sub.id)
    await db.refresh(task)
    return await _read(db, task)
