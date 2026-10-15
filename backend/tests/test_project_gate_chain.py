"""A lesson opens only when EVERY earlier project lesson is passed — not just the one right before it."""
import uuid

from sqlalchemy import insert, select

from app.core.security import create_access_token
from app.db.database import AsyncSessionLocal
from app.models.course import Course, student_courses
from app.models.lesson import Lesson
from app.models.project import Project
from app.models.submission import Submission
from app.models.user import Student, UserRole


async def _setup(async_client):
    uid = uuid.uuid4().hex[:8]
    ids = []
    for who in ("t", "s"):
        reg = await async_client.post("/api/v1/auth/register", json={
            "username": f"gc{who}_{uid}", "email": f"gc{who}_{uid}@example.com", "password": "securepass123"})
        ids.append(reg.json()["user"]["id"])
    tid, sid = ids
    async with AsyncSessionLocal() as db:
        t = (await db.execute(select(Student).where(Student.id == tid))).scalar_one()
        t.role = UserRole.teacher
        c = Course(title="Chain", description="d", instructor_id=tid, difficulty_level="Beginner",
                   duration_weeks=1, max_points=10, is_active=True, is_published=True)
        db.add(c)
        await db.flush()
        ls = [Lesson(course_id=c.id, title=f"L{i}", order=i, is_active=True, is_published=True,
                     task_title="Loyiha" if i == 0 else None) for i in range(3)]
        db.add_all(ls)
        await db.flush()
        await db.execute(insert(student_courses).values(student_id=sid, course_id=c.id))
        await db.commit()
        return sid, c.id, [l.id for l in ls], {"Authorization": f"Bearer {create_access_token(subject=sid)}"}


async def _status(async_client, h, cid, lid):
    return (await async_client.get(f"/api/v1/courses/{cid}/lessons/{lid}", headers=h)).status_code


async def test_a_rejected_project_closes_every_later_lesson_not_only_the_next(async_client):
    sid, cid, (l0, l1, l2), h = await _setup(async_client)
    assert await _status(async_client, h, cid, l0) == 200
    assert await _status(async_client, h, cid, l1) == 403
    assert await _status(async_client, h, cid, l2) == 403   # lesson 1 has no project — the old rule let this through

    async with AsyncSessionLocal() as db:
        p = Project(student_id=sid, title="p", description="d", difficulty_level="Beginner",
                    status="Rejected", points_earned=0)
        db.add(p)
        await db.flush()
        db.add(Submission(project_id=p.id, student_id=sid, lesson_id=l0, status="Rejected"))
        await db.commit()
        pid = p.id
    assert await _status(async_client, h, cid, l2) == 403

    async with AsyncSessionLocal() as db:
        p = (await db.execute(select(Project).where(Project.id == pid))).scalar_one()
        p.status, p.points_earned = "Approved", 85
        await db.commit()
    assert await _status(async_client, h, cid, l1) == 200
    assert await _status(async_client, h, cid, l2) == 200
