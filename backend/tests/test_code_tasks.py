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


# ── Task 2: teacher side ────────────────────────────────────────────────────

def _body(student_id, **over):
    return {"student_id": student_id, "title": "Sort a list", "description": "Write bubble sort.",
            "language": "python", **over}


async def _create(client, tid, sid, **over):
    r = await client.post(f"{TEACHER_API}/", headers=_h(tid), json=_body(sid, **over))
    assert r.status_code == 201, r.text
    return r.json()


async def _set(task_id, **fields):
    async with AsyncSessionLocal() as db:
        t = await db.get(CodeTask, task_id)
        for k, v in fields.items():
            setattr(t, k, v)
        await db.commit()


async def test_teacher_creates_a_task_for_own_student(async_client):
    tid, sid = await _teacher_with_student()
    task = await _create(async_client, tid, sid, lang="ru")
    assert task["status"] == "assigned" and task["max_points"] == 20 and task["student_id"] == sid
    async with AsyncSessionLocal() as db:
        assert (await db.get(CodeTask, task["id"])).review_lang == "ru"


async def test_creating_for_a_student_outside_my_scope_is_404(async_client):
    tid, _ = await _teacher_with_student()
    _, stranger = await _teacher_with_student()
    r = await async_client.post(f"{TEACHER_API}/", headers=_h(tid), json=_body(stranger))
    assert r.status_code == 404


async def test_invalid_input_is_422(async_client):
    tid, sid = await _teacher_with_student()
    for over in ({"language": "cobol"}, {"max_points": 0}, {"max_points": 101}, {"title": ""},
                 {"title": "x" * 201}, {"description": "x" * 10_001}, {"starter_code": "x" * 100_001}):
        r = await async_client.post(f"{TEACHER_API}/", headers=_h(tid), json=_body(sid, **over))
        assert r.status_code == 422, over


async def test_a_student_cannot_use_the_teacher_api(async_client):
    tid, sid = await _teacher_with_student()
    r = await async_client.post(f"{TEACHER_API}/", headers=_h(sid), json=_body(sid))
    assert r.status_code == 403


async def test_list_for_a_student_shows_only_my_tasks_newest_first(async_client):
    tid, sid = await _teacher_with_student()
    other = await _user(teacher=True)
    async with AsyncSessionLocal() as db:                       # the same student also sits in another teacher's group
        g = Group(name=f"g_{uuid.uuid4().hex[:6]}", teacher_id=other)
        db.add(g)
        await db.flush()
        await db.execute(student_groups.insert().values(student_id=sid, group_id=g.id))
        await db.commit()
    first = await _create(async_client, tid, sid, title="first")
    second = await _create(async_client, tid, sid, title="second")
    theirs = await async_client.post(f"{TEACHER_API}/", headers=_h(other), json=_body(sid, title="theirs"))
    assert theirs.status_code == 201
    rows = (await async_client.get(f"{TEACHER_API}/student/{sid}", headers=_h(tid))).json()
    assert [r["title"] for r in rows] == ["second", "first"]
    assert {r["id"] for r in rows} == {first["id"], second["id"]}
    stranger = (await _teacher_with_student())[0]
    assert (await async_client.get(f"{TEACHER_API}/student/{sid}", headers=_h(stranger))).status_code == 404


async def test_another_teachers_task_is_404_on_read_patch_delete(async_client):
    tid, sid = await _teacher_with_student()
    task = await _create(async_client, tid, sid)
    other = await _user(teacher=True)
    assert (await async_client.get(f"{TEACHER_API}/{task['id']}", headers=_h(other))).status_code == 404
    assert (await async_client.patch(f"{TEACHER_API}/{task['id']}", headers=_h(other), json={"title": "x"})).status_code == 404
    assert (await async_client.delete(f"{TEACHER_API}/{task['id']}", headers=_h(other))).status_code == 404


async def test_detail_lists_submissions_with_ai_and_integrity_fields(async_client):
    tid, sid = await _teacher_with_student()
    task = await _create(async_client, tid, sid)
    async with AsyncSessionLocal() as db:
        db.add(CodeTaskSubmission(task_id=task["id"], attempt_no=1, code="print(1)", typed_chars=5, pasted_chars=45,
                                  paste_events=1, active_seconds=90, ai_status="done", ai_review={"summary": "ok"}))
        await db.commit()
    body = (await async_client.get(f"{TEACHER_API}/{task['id']}", headers=_h(tid))).json()
    sub = body["submissions"][0]
    assert sub["code"] == "print(1)" and sub["pasted_chars"] == 45 and sub["ai_review"] == {"summary": "ok"}


async def test_patch_and_delete_only_before_submission(async_client):
    tid, sid = await _teacher_with_student()
    task = await _create(async_client, tid, sid)
    r = await async_client.patch(f"{TEACHER_API}/{task['id']}", headers=_h(tid), json={"title": "New", "max_points": 30})
    assert r.status_code == 200 and r.json()["title"] == "New" and r.json()["max_points"] == 30
    assert (await async_client.delete(f"{TEACHER_API}/{task['id']}", headers=_h(tid))).status_code == 204
    again = await _create(async_client, tid, sid)
    await _set(again["id"], status="submitted")
    assert (await async_client.patch(f"{TEACHER_API}/{again['id']}", headers=_h(tid), json={"title": "x"})).status_code == 409
    assert (await async_client.delete(f"{TEACHER_API}/{again['id']}", headers=_h(tid))).status_code == 409
    returned = await _create(async_client, tid, sid)
    await _set(returned["id"], status="returned")
    async with AsyncSessionLocal() as db:
        db.add(CodeTaskSubmission(task_id=returned["id"], attempt_no=1, code="x"))
        await db.commit()
    assert (await async_client.delete(f"{TEACHER_API}/{returned['id']}", headers=_h(tid))).status_code == 409
