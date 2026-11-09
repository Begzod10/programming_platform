"""Teacher side of code tasks: give a student a task, read what came back. Grading is added next to it."""
from datetime import datetime
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_instructor, get_db
from app.models.code_task import MAX_CODE_CHARS, CodeTask
from app.models.user import Student
from app.services import code_task_service as svc

router = APIRouter()

Language = Literal["html", "css", "javascript", "python", "sql", "json", "text"]


def _strip_required(v: str) -> str:
    v = (v or "").strip()
    if not v:
        raise ValueError("bo'sh bo'lmasligi kerak")
    return v


class TaskCreate(BaseModel):
    student_id: int
    title: str = Field(max_length=200)
    description: str = Field(max_length=10_000)
    language: Language
    starter_code: Optional[str] = Field(default=None, max_length=MAX_CODE_CHARS)
    max_points: int = Field(default=20, ge=1, le=100)
    deadline: Optional[datetime] = None
    lang: Literal["uz", "ru"] = "uz"

    _t = field_validator("title", "description")(_strip_required)


class TaskPatch(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=10_000)
    language: Optional[Language] = None
    starter_code: Optional[str] = Field(default=None, max_length=MAX_CODE_CHARS)
    max_points: Optional[int] = Field(default=None, ge=1, le=100)
    deadline: Optional[datetime] = None

    @field_validator("title", "description")
    @classmethod
    def _not_blank(cls, v):
        return v if v is None else _strip_required(v)


class SubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    attempt_no: int
    submitted_at: datetime
    code: str
    ai_status: str
    ai_review: Optional[dict] = None
    started_at: Optional[datetime] = None
    active_seconds: int
    typed_chars: int
    pasted_chars: int
    paste_events: int
    return_feedback: Optional[str] = None
    returned_at: Optional[datetime] = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    title: str
    description: str
    language: str
    starter_code: Optional[str] = None
    max_points: int
    deadline: Optional[datetime] = None
    status: str
    graded_points: Optional[int] = None
    teacher_feedback: Optional[str] = None
    graded_at: Optional[datetime] = None
    created_at: datetime


class TaskDetail(TaskRead):
    submissions: List[SubmissionRead]


async def _detail(db: AsyncSession, task: CodeTask) -> TaskDetail:
    subs = await svc.submissions_of(db, task.id)
    return TaskDetail(**TaskRead.model_validate(task).model_dump(),
                      submissions=[SubmissionRead.model_validate(s) for s in subs])


def _http(exc: Exception) -> HTTPException:
    if isinstance(exc, svc.TaskNotFound):
        return HTTPException(status_code=404, detail="Vazifa topilmadi")
    if isinstance(exc, svc.WrongState):
        return HTTPException(status_code=409, detail="Vazifa hozirgi holatda bu amalni qabul qilmaydi")
    return HTTPException(status_code=422, detail="Noto'g'ri qiymat")


@router.post("/", response_model=TaskRead, status_code=201)
async def create_task(body: TaskCreate, teacher: Student = Depends(get_current_instructor),
                      db: AsyncSession = Depends(get_db)):
    try:
        return await svc.create_task(
            db, teacher.id, student_id=body.student_id, title=body.title, description=body.description,
            language=body.language, starter_code=body.starter_code, max_points=body.max_points,
            deadline=body.deadline, review_lang=body.lang)
    except (svc.TaskNotFound, svc.InvalidInput) as e:
        raise _http(e)


# declared before "/{task_id}" so "student" is never parsed as an id
@router.get("/student/{student_id}", response_model=List[TaskRead])
async def list_for_student(student_id: int, teacher: Student = Depends(get_current_instructor),
                           db: AsyncSession = Depends(get_db)):
    try:
        return await svc.list_for_teacher(db, teacher.id, student_id)
    except svc.TaskNotFound as e:
        raise _http(e)


@router.get("/{task_id}", response_model=TaskDetail)
async def read_task(task_id: int, teacher: Student = Depends(get_current_instructor),
                    db: AsyncSession = Depends(get_db)):
    try:
        return await _detail(db, await svc.get_teacher_task(db, teacher.id, task_id))
    except svc.TaskNotFound as e:
        raise _http(e)


@router.patch("/{task_id}", response_model=TaskRead)
async def patch_task(task_id: int, body: TaskPatch, teacher: Student = Depends(get_current_instructor),
                     db: AsyncSession = Depends(get_db)):
    try:
        task = await svc.get_teacher_task(db, teacher.id, task_id, for_update=True)
        return await svc.update_task(db, task, **body.model_dump(exclude_unset=True))
    except (svc.TaskNotFound, svc.WrongState, svc.InvalidInput) as e:
        raise _http(e)


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, teacher: Student = Depends(get_current_instructor),
                      db: AsyncSession = Depends(get_db)):
    try:
        task = await svc.get_teacher_task(db, teacher.id, task_id, for_update=True)
        await svc.delete_task(db, task)
    except (svc.TaskNotFound, svc.WrongState) as e:
        raise _http(e)
    return Response(status_code=204)


class GradeBody(BaseModel):
    points: int = Field(ge=0, le=100)
    feedback: Optional[str] = Field(default=None, max_length=5000)


class ReturnBody(BaseModel):
    feedback: str = Field(max_length=5000)


@router.post("/{task_id}/grade", response_model=TaskRead)
async def grade_task(task_id: int, body: GradeBody, teacher: Student = Depends(get_current_instructor),
                     db: AsyncSession = Depends(get_db)):
    try:
        task = await svc.get_teacher_task(db, teacher.id, task_id, for_update=True)
        return await svc.grade(db, task, points=body.points, feedback=body.feedback)
    except (svc.TaskNotFound, svc.WrongState, svc.InvalidInput) as e:
        raise _http(e)


@router.post("/{task_id}/return", response_model=TaskRead)
async def return_task(task_id: int, body: ReturnBody, teacher: Student = Depends(get_current_instructor),
                      db: AsyncSession = Depends(get_db)):
    try:
        task = await svc.get_teacher_task(db, teacher.id, task_id, for_update=True)
        return await svc.return_task(db, task, feedback=body.feedback)
    except (svc.TaskNotFound, svc.WrongState, svc.InvalidInput) as e:
        raise _http(e)
