"""GET /teacher/students/{id}/dictionary: a teacher reads the words a student saved, to ask them out loud."""
import uuid
from datetime import datetime

import pytest_asyncio
from sqlalchemy import update

from app.models.dictionary import UserDictionary
from app.models.group import Group, student_groups
from app.models.user import Student


async def _register(async_client, prefix):
    uid = uuid.uuid4().hex[:8]
    username, password = f"{prefix}_{uid}", "securepass123"
    reg = await async_client.post("/api/v1/auth/register", json={
        "username": username, "email": f"{username}@example.com", "password": password})
    assert reg.status_code == 201, reg.text
    return reg.json()["user"]["id"], username, password


async def _headers(async_client, username, password):
    login = await async_client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest_asyncio.fixture
async def setup(async_client, db_session):
    teacher_id, t_name, t_pw = await _register(async_client, "dtteacher")
    other_id, o_name, o_pw = await _register(async_client, "dtother")
    student_id, s_name, s_pw = await _register(async_client, "dtstudent")
    await db_session.execute(update(Student).where(Student.id.in_([teacher_id, other_id])).values(role="teacher"))
    group = Group(name="Dict Group", teacher_id=teacher_id)
    db_session.add(group)
    await db_session.flush()
    await db_session.execute(student_groups.insert().values(student_id=student_id, group_id=group.id))
    db_session.add_all([
        UserDictionary(student_id=student_id, word="mutation", context="A mutation changes state.", lang="uz",
                       review_count=3, correct_count=1, incorrect_count=2, created_at=datetime(2026, 10, 1)),
        UserDictionary(student_id=student_id, word="итератор", context=None, lang="ru", created_at=datetime(2026, 10, 2)),
        UserDictionary(student_id=student_id, word="closure", context="x", lang="uz", created_at=datetime(2026, 10, 3)),
    ])
    await db_session.commit()
    return {
        "student_id": student_id,
        "teacher": await _headers(async_client, t_name, t_pw),
        "other": await _headers(async_client, o_name, o_pw),
        "student": await _headers(async_client, s_name, s_pw),
    }


async def test_teacher_sees_the_words_newest_first_with_review_stats(async_client, setup):
    resp = await async_client.get(f"/api/v1/teacher/students/{setup['student_id']}/dictionary", headers=setup["teacher"])
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["student_id"] == setup["student_id"] and data["total"] == 3
    assert [w["word"] for w in data["words"]] == ["closure", "итератор", "mutation"]
    mutation = data["words"][2]
    assert (mutation["review_count"], mutation["correct_count"], mutation["incorrect_count"]) == (3, 1, 2)
    assert mutation["context"] == "A mutation changes state." and mutation["lang"] == "uz"


async def test_language_filter(async_client, setup):
    resp = await async_client.get(
        f"/api/v1/teacher/students/{setup['student_id']}/dictionary?lang=ru", headers=setup["teacher"])
    assert [w["word"] for w in resp.json()["words"]] == ["итератор"]


async def test_another_teachers_student_is_a_404(async_client, setup):
    resp = await async_client.get(f"/api/v1/teacher/students/{setup['student_id']}/dictionary", headers=setup["other"])
    assert resp.status_code == 404


async def test_students_and_anonymous_users_are_refused(async_client, setup):
    url = f"/api/v1/teacher/students/{setup['student_id']}/dictionary"
    assert (await async_client.get(url)).status_code == 401
    assert (await async_client.get(url, headers=setup["student"])).status_code in (401, 403)
