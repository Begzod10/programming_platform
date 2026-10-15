"""Lesson sections always carry a stable, unique id (bulk-imported lessons had none, which broke the
student page's table of contents: every block shared `undefined`)."""
import json
import uuid

from sqlalchemy import select

from app.core.security import create_access_token
from app.db.database import AsyncSessionLocal
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.user import Student, UserRole
from app.utils.lesson_sections import ensure_section_ids, section_id

NO_IDS = json.dumps([{"type": "text", "label": "Nazariya", "html": "<p>x</p>"}, {"type": "code", "label": "Misol"},
                     {"type": "code", "label": "Kod"}, {"type": "exercise", "label": "Mashqlar"}])


def test_missing_blank_and_duplicate_ids_are_filled_in():
    out, changed = ensure_section_ids(529, NO_IDS)
    ids = [s["id"] for s in json.loads(out)]
    assert changed and ids == ["s529-0", "s529-1", "s529-2", "s529-3"] and ids[0] == section_id(529, 0)

    out, changed = ensure_section_ids(7, json.dumps([{"id": "a"}, {"id": ""}, {"id": "a"}, {"id": 5}]))
    assert changed and [s["id"] for s in json.loads(out)] == ["a", "s7-1", "s7-2", 5]


def test_a_lesson_that_already_has_ids_is_left_exactly_as_it_is():
    raw = json.dumps([{"id": "t1", "type": "text"}, {"id": "p1", "type": "project"}])
    assert ensure_section_ids(1, raw) == (raw, False)


def test_garbage_is_not_touched():
    for raw in (None, "", "not json", "{}", '"x"', "[1, 2]"):
        out, changed = ensure_section_ids(1, raw)
        assert out == raw and changed is False


async def _teacher_and_course(async_client):
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post("/api/v1/auth/register", json={
        "username": f"ls_{uid}", "email": f"ls_{uid}@example.com", "password": "securepass123"})
    tid = reg.json()["user"]["id"]
    async with AsyncSessionLocal() as db:
        t = (await db.execute(select(Student).where(Student.id == tid))).scalar_one()
        t.role = UserRole.teacher
        c = Course(title="Sections", description="d", instructor_id=tid, difficulty_level="Beginner",
                   duration_weeks=1, max_points=10, is_active=True, is_published=True)
        db.add(c)
        await db.commit()
        await db.refresh(c)
        return tid, c.id, {"Authorization": f"Bearer {create_access_token(subject=tid)}"}


async def test_the_api_serves_ids_for_an_old_lesson_that_has_none(async_client):
    tid, cid, h = await _teacher_and_course(async_client)
    async with AsyncSessionLocal() as db:
        lesson = Lesson(course_id=cid, title="Old", order=0, sections_json=NO_IDS, is_active=True, is_published=True)
        db.add(lesson)
        await db.commit()
        await db.refresh(lesson)
        lid = lesson.id
    one = (await async_client.get(f"/api/v1/courses/{cid}/lessons/{lid}", headers=h)).json()
    ids = [s["id"] for s in json.loads(one["sections_json"])]
    assert ids == [f"s{lid}-{i}" for i in range(4)]
    listed = (await async_client.get(f"/api/v1/courses/{cid}/lessons", headers=h)).json()
    assert [s["id"] for s in json.loads(next(l for l in listed if l["id"] == lid)["sections_json"])] == ids


async def test_creating_and_editing_a_lesson_stores_the_ids(async_client):
    tid, cid, h = await _teacher_and_course(async_client)
    r = await async_client.post(f"/api/v1/courses/{cid}/lessons", headers=h,
                                json={"title": "New", "order": 0, "sections_json": NO_IDS})
    assert r.status_code == 201, r.text
    lid = r.json()["id"]
    async with AsyncSessionLocal() as db:
        stored = (await db.execute(select(Lesson.sections_json).where(Lesson.id == lid))).scalar_one()
    assert [s["id"] for s in json.loads(stored)] == [f"s{lid}-{i}" for i in range(4)]

    r = await async_client.put(f"/api/v1/courses/{cid}/lessons/{lid}", headers=h,
                               json={"sections_json": json.dumps([{"type": "text"}, {"type": "code"}])})
    assert r.status_code == 200, r.text
    async with AsyncSessionLocal() as db:
        stored = (await db.execute(select(Lesson.sections_json).where(Lesson.id == lid))).scalar_one()
    assert [s["id"] for s in json.loads(stored)] == [f"s{lid}-0", f"s{lid}-1"]
