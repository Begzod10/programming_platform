"""Student-side class ("sinf") filter on the leaderboard — mirrors the
group_id filter the teacher rankings page already has
(StudentRankings.js / GET /teacher/students/rankings), just for the
student-facing GET /rankings/leaderboard, plus the new GET
/rankings/my-groups endpoint that feeds the filter dropdown its options
(GET /groups/ is teacher-only, so students need their own equivalent).
"""
import uuid

from httpx import AsyncClient

from app.models.group import Group, student_groups


async def _register_and_login(async_client: AsyncClient, prefix: str):
    uid = uuid.uuid4().hex[:8]
    username, password = f"{prefix}_{uid}", "securepass123"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{prefix}_{uid}@example.com", "password": password},
    )
    assert reg.status_code == 201, f"Register failed: {reg.text}"
    student_id = reg.json()["user"]["id"]

    login = await async_client.post(
        "/api/v1/auth/login", json={"username": username, "password": password},
    )
    assert login.status_code == 200, f"Login failed: {login.text}"
    token = login.json()["access_token"]
    return student_id, {"Authorization": f"Bearer {token}"}


async def _make_group(db_session, name: str, teacher_id: int = None) -> Group:
    group = Group(name=name, teacher_id=teacher_id)
    db_session.add(group)
    await db_session.flush()
    await db_session.commit()
    return group


async def _add_to_group(db_session, student_id: int, group_id: int) -> None:
    await db_session.execute(student_groups.insert().values(student_id=student_id, group_id=group_id))
    await db_session.commit()


# ── GET /rankings/leaderboard?group_id= ──────────────────────────────────


async def test_leaderboard_with_group_id_returns_200(async_client: AsyncClient):
    resp = await async_client.get("/api/v1/rankings/leaderboard?group_id=999999")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_leaderboard_group_id_filters_to_only_that_group(async_client, db_session):
    teacher_id, _ = await _register_and_login(async_client, "teacher")
    in_group_id, _ = await _register_and_login(async_client, "ingroup")
    outside_id, _ = await _register_and_login(async_client, "outside")

    group = await _make_group(db_session, "7-green", teacher_id=teacher_id)
    await _add_to_group(db_session, in_group_id, group.id)
    # outside_id intentionally left out of the group.

    resp = await async_client.get(f"/api/v1/rankings/leaderboard?group_id={group.id}&limit=100")
    assert resp.status_code == 200
    ids = {row["student_id"] for row in resp.json()}
    assert in_group_id in ids
    assert outside_id not in ids


# ── GET /rankings/my-groups ───────────────────────────────────────────────


async def test_my_groups_requires_auth(async_client: AsyncClient):
    resp = await async_client.get("/api/v1/rankings/my-groups")
    assert resp.status_code == 401


async def test_my_groups_returns_only_the_students_own_groups(async_client, db_session):
    teacher_id, _ = await _register_and_login(async_client, "teacher")
    student_id, student_headers = await _register_and_login(async_client, "student")

    my_group = await _make_group(db_session, "7-green", teacher_id=teacher_id)
    other_group = await _make_group(db_session, "8-blue", teacher_id=teacher_id)
    await _add_to_group(db_session, student_id, my_group.id)
    # other_group intentionally has no membership for this student.

    resp = await async_client.get("/api/v1/rankings/my-groups", headers=student_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert [g["id"] for g in data] == [my_group.id]
    assert data[0]["name"] == "7-green"


async def test_my_groups_can_return_more_than_one_group(async_client, db_session):
    """A student can legitimately belong to multiple classes (different
    subjects/teachers) — the endpoint must not assume exactly one."""
    teacher_id, _ = await _register_and_login(async_client, "teacher")
    student_id, student_headers = await _register_and_login(async_client, "student")

    group_a = await _make_group(db_session, "7-green", teacher_id=teacher_id)
    group_b = await _make_group(db_session, "9-red", teacher_id=teacher_id)
    await _add_to_group(db_session, student_id, group_a.id)
    await _add_to_group(db_session, student_id, group_b.id)

    resp = await async_client.get("/api/v1/rankings/my-groups", headers=student_headers)
    assert resp.status_code == 200
    names = {g["name"] for g in resp.json()}
    assert names == {"7-green", "9-red"}


async def test_my_groups_empty_when_student_has_no_class(async_client: AsyncClient):
    _student_id, student_headers = await _register_and_login(async_client, "lonestudent")
    resp = await async_client.get("/api/v1/rankings/my-groups", headers=student_headers)
    assert resp.status_code == 200
    assert resp.json() == []
