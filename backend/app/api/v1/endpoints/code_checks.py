"""Code-check quizzes: the student's side (take the quiz) and the teacher's side (the queue).

See services/code_check_service.py for what a check is and why it never changes points by itself.
"""
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_instructor, get_current_student, get_db
from app.models.code_check import ProjectCodeCheck
from app.models.project import Project
from app.models.user import Student
from app.services import code_check_service as svc
from app.utils.datetime_utils import utcnow

router = APIRouter()            # /code-checks        (students)
teacher_router = APIRouter()    # /teacher/code-checks


def _fail(e: svc.CheckError):
    raise HTTPException(status_code=e.status, detail=e.message)


async def _own_check(db: AsyncSession, check_id: int, student: Student) -> ProjectCodeCheck:
    check = (await db.execute(select(ProjectCodeCheck).where(ProjectCodeCheck.id == check_id))).scalar_one_or_none()
    if check is None or check.student_id != student.id:
        raise HTTPException(status_code=404, detail="Tekshiruv topilmadi")
    return check


# ── student ──────────────────────────────────────────────────────────────────

@router.get("/mine")
async def my_pending_checks(student: Student = Depends(get_current_student), db: AsyncSession = Depends(get_db)):
    """Quizzes waiting for this student (open and not past their deadline)."""
    rows = (await db.execute(
        select(ProjectCodeCheck, Project.title)
        .join(Project, Project.id == ProjectCodeCheck.project_id)
        .where(ProjectCodeCheck.student_id == student.id, ProjectCodeCheck.status == "pending",
               ProjectCodeCheck.expires_at > utcnow())
        .order_by(ProjectCodeCheck.created_at.desc()))).all()
    return [{"id": c.id, "project_id": c.project_id, "project_title": title,
             "expires_at": svc._aware(c.expires_at).isoformat(), "started": c.started_at is not None,
             "total_questions": c.total_questions, "seconds_per_question": svc.SECONDS_PER_QUESTION}
            for c, title in rows]


@router.post("/{check_id}/start")
async def start_check(check_id: int, lang: str = Query("uz", max_length=2),
                      student: Student = Depends(get_current_student), db: AsyncSession = Depends(get_db)):
    check = await _own_check(db, check_id, student)
    try:
        return await svc.start_check(db, check, lang)
    except svc.CheckError as e:
        _fail(e)


class SubmitBody(BaseModel):
    answers: list[Optional[int]] = Field(default_factory=list, max_length=10)
    blur_count: int = Field(0, ge=0, le=1000)
    times_ms: list[int] = Field(default_factory=list, max_length=10)


@router.post("/{check_id}/submit")
async def submit_check(check_id: int, body: SubmitBody,
                       student: Student = Depends(get_current_student), db: AsyncSession = Depends(get_db)):
    check = await _own_check(db, check_id, student)
    try:
        return await svc.submit_check(db, check, body.answers, body.blur_count, body.times_ms)
    except svc.CheckError as e:
        _fail(e)


# ── teacher ──────────────────────────────────────────────────────────────────

def _teacher_row(c: ProjectCodeCheck, project: Optional[Project], st: Optional[Student]) -> dict:
    questions = json.loads(c.questions_json) if c.questions_json else []
    answers = json.loads(c.answers_json) if c.answers_json else []
    return {
        "id": c.id, "status": c.status, "reason": c.reason, "needs_teacher": c.needs_teacher,
        "student": {"id": c.student_id, "username": st.username if st else None, "full_name": st.full_name if st else None},
        "project": {"id": c.project_id, "title": project.title if project else None,
                    "points_earned": project.points_earned if project else None, "grade": project.grade if project else None},
        "code_lines": c.code_lines, "pace": c.pace, "gap_minutes": None if c.gap_seconds is None else round(c.gap_seconds / 60, 1),
        "correct": c.correct_count, "total": c.total_questions, "blur_count": c.blur_count, "duration_seconds": c.duration_seconds,
        "created_at": svc._aware(c.created_at).isoformat(),
        "finished_at": svc._aware(c.finished_at).isoformat() if c.finished_at else None,
        "resolution": c.resolution, "teacher_note": c.teacher_note,
        # the questions with the right answer and what the student chose: material for the oral talk
        "questions": [{"q": q["uz"]["q"], "options": q["uz"]["options"], "correct": q["correct"],
                       "answer": answers[i] if i < len(answers) else None} for i, q in enumerate(questions)],
    }


@teacher_router.get("")
async def teacher_queue(all: bool = Query(False), limit: int = Query(100, ge=1, le=300),
                        teacher: Student = Depends(get_current_instructor), db: AsyncSession = Depends(get_db)):
    """Checks that need a teacher (failed / not taken / unavailable); `all=true` lists everything."""
    await svc.expire_old_checks(db)
    q = (select(ProjectCodeCheck, Project, Student)
         .join(Project, Project.id == ProjectCodeCheck.project_id)
         .join(Student, Student.id == ProjectCodeCheck.student_id)
         .order_by(ProjectCodeCheck.created_at.desc()).limit(limit))
    if not all:
        q = q.where(ProjectCodeCheck.needs_teacher.is_(True), ProjectCodeCheck.resolution.is_(None))
    rows = (await db.execute(q)).all()
    return [_teacher_row(c, p, s) for c, p, s in rows]


class ResolveBody(BaseModel):
    action: str = Field(..., pattern="^(dismiss|revoke_points)$")
    note: Optional[str] = Field(None, max_length=1000)


@teacher_router.post("/{check_id}/resolve")
async def teacher_resolve(check_id: int, body: ResolveBody,
                          teacher: Student = Depends(get_current_instructor), db: AsyncSession = Depends(get_db)):
    check = (await db.execute(select(ProjectCodeCheck).where(ProjectCodeCheck.id == check_id))).scalar_one_or_none()
    if check is None:
        raise HTTPException(status_code=404, detail="Tekshiruv topilmadi")
    try:
        await svc.resolve_check(db, check, teacher, body.action, body.note)
    except svc.CheckError as e:
        _fail(e)
    project = (await db.execute(select(Project).where(Project.id == check.project_id))).scalar_one_or_none()
    st = (await db.execute(select(Student).where(Student.id == check.student_id))).scalar_one_or_none()
    return _teacher_row(check, project, st)
