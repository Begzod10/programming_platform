"""Teacher code tasks: a teacher gives a student a coding task, the student writes and submits code, the teacher
grades or returns it. See docs/superpowers/specs/2026-11-09-teacher-code-tasks-design.md."""
import asyncio
import uuid
from datetime import timedelta

from sqlalchemy import delete, func, select

from app.core.security import create_access_token
from app.db.database import AsyncSessionLocal
from app.models.code_task import CodeTask, CodeTaskSubmission
from app.models.group import Group, student_groups
from app.models.user import Student, UserRole
from app.utils.datetime_utils import utcnow

TEACHER_API = "/api/v1/teacher/code-tasks"
STUDENT_API = "/api/v1/code-tasks"


async def _user(*, teacher=False):
    uid = uuid.uuid4().hex[:8]
    async with AsyncSessionLocal() as db:
        s = Student(username=f"ct_{uid}", email=f"ct_{uid}@example.com", hashed_password="x",
                    full_name=f"User {uid}", role=UserRole.teacher if teacher else UserRole.student)
        db.add(s)
        await db.commit()
        return s.id


def _h(user_id):
    return {"Authorization": f"Bearer {create_access_token(subject=user_id)}"}


async def _teacher_with_student():
    """(teacher_id, student_id): the student sits in a group the teacher owns."""
    tid, sid = await _user(teacher=True), await _user()
    async with AsyncSessionLocal() as db:
        g = Group(name=f"g_{uuid.uuid4().hex[:6]}", teacher_id=tid)
        db.add(g)
        await db.flush()
        await db.execute(student_groups.insert().values(student_id=sid, group_id=g.id))
        await db.commit()
    return tid, sid


async def test_tables_exist_and_defaults_apply():
    tid, sid = await _user(teacher=True), await _user()
    async with AsyncSessionLocal() as db:
        t = CodeTask(teacher_id=tid, student_id=sid, title="T", description="D", language="python")
        db.add(t)
        await db.commit()
        await db.refresh(t)
        assert t.status == "assigned" and t.max_points == 20 and t.review_lang == "uz"
        assert t.graded_points is None and t.draft_code is None
        sub = CodeTaskSubmission(task_id=t.id, attempt_no=1, code="x")
        db.add(sub)
        await db.commit()
        await db.refresh(sub)
        assert sub.ai_status == "pending" and sub.typed_chars == 0 and sub.pasted_chars == 0
