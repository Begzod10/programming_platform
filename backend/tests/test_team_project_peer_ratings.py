"""Tests for GET /teams/{team_id}/peer-ratings (app/api/v1/endpoints/
team_project.py) — closes a real gap flagged by a full feature audit:
peer ratings were collected and already fed team_project_points_service's
bonus modifier, but nothing let a teacher actually see them, so a member's
bonus could get halved with no way to find out why.

Also covers why this is a NEW endpoint rather than a field on TeamRead:
TeamRead is shared with the student-facing GET /team-projects/my and the
team-scoped realtime WS channel a student's own team is pushed over, so
embedding rater identity/comments there would leak "who rated me what" to
the person being rated.
"""
import uuid

import pytest_asyncio
from sqlalchemy import select

from app.models.group import Group, student_groups
from app.models.team_project import TeamProjectPeerRating, TeamStatus
from app.services.team_project_service import create_team_project
from unittest.mock import patch

BASE = "/api/v1/team-projects"


async def _register(async_client, prefix: str) -> tuple[int, str]:
    uid = uuid.uuid4().hex[:8]
    username = f"{prefix}_{uid}"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "pass12345"},
    )
    assert reg.status_code == 201, reg.text
    return reg.json()["user"]["id"], username


async def _login_headers(async_client, username: str, password: str = "pass12345") -> dict:
    login = await async_client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest_asyncio.fixture
async def rated_team(async_client, db_session):
    """1 owning teacher, 1 other teacher, 2 students on a submitted team
    with one peer rating (student B rating student A 4/5, with a
    comment) already in the DB."""
    from app.models.user import Student

    uid = uuid.uuid4().hex[:8]

    owner_id, owner_username = await _register(async_client, f"tpr_owner_{uid}")
    other_teacher_id, other_teacher_username = await _register(async_client, f"tpr_other_{uid}")
    student_a_id, student_a_username = await _register(async_client, f"tpr_a_{uid}")
    student_b_id, student_b_username = await _register(async_client, f"tpr_b_{uid}")

    for tid in (owner_id, other_teacher_id):
        t = (await db_session.execute(select(Student).where(Student.id == tid))).scalar_one()
        t.role = "teacher"

    group = Group(name="PR Group", teacher_id=owner_id)
    db_session.add(group)
    await db_session.flush()
    for sid in (student_a_id, student_b_id):
        await db_session.execute(student_groups.insert().values(student_id=sid, group_id=group.id))
    await db_session.commit()

    with patch(
        "app.services.team_project_service.spawn_background_task",
        side_effect=lambda coro: coro.close(),
    ):
        tp = await create_team_project(
            db_session, group_id=group.id, course_id=None, teacher_id=owner_id,
            team_size=2, deadline_days=14,
        )
    await db_session.commit()

    from app.models.team_project import TeamProjectTeam
    team = (await db_session.execute(
        select(TeamProjectTeam).where(TeamProjectTeam.team_project_id == tp.id)
    )).scalars().one()
    team.status = TeamStatus.submitted
    db_session.add(TeamProjectPeerRating(
        team_id=team.id, rater_student_id=student_b_id, rated_student_id=student_a_id,
        score=4, comment="Yaxshi ishladi",
    ))
    await db_session.commit()

    return {
        "team_id": team.id,
        "owner_headers": await _login_headers(async_client, owner_username),
        "other_teacher_headers": await _login_headers(async_client, other_teacher_username),
        "student_headers": await _login_headers(async_client, student_a_username),
        "student_a_id": student_a_id, "student_b_id": student_b_id,
        "student_a_username": student_a_username, "student_b_username": student_b_username,
    }


async def test_owning_teacher_sees_the_rating_with_names_and_comment(async_client, rated_team):
    fx = rated_team
    resp = await async_client.get(
        f"{BASE}/teams/{fx['team_id']}/peer-ratings", headers=fx["owner_headers"],
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 1
    rating = data[0]
    assert rating["rater_student_id"] == fx["student_b_id"]
    assert rating["rater_name"] == fx["student_b_username"]
    assert rating["rated_student_id"] == fx["student_a_id"]
    assert rating["rated_name"] == fx["student_a_username"]
    assert rating["score"] == 4
    assert rating["comment"] == "Yaxshi ishladi"


async def test_non_owning_teacher_is_rejected(async_client, rated_team):
    fx = rated_team
    resp = await async_client.get(
        f"{BASE}/teams/{fx['team_id']}/peer-ratings", headers=fx["other_teacher_headers"],
    )
    assert resp.status_code == 403


async def test_student_cannot_view_the_endpoint_at_all(async_client, rated_team):
    """Not just "can't see other teams" — students have no route to this
    data whatsoever, per PeerRatingRead's docstring on why it's not on
    TeamRead."""
    fx = rated_team
    resp = await async_client.get(
        f"{BASE}/teams/{fx['team_id']}/peer-ratings", headers=fx["student_headers"],
    )
    assert resp.status_code in (401, 403)


async def test_unknown_team_returns_404(async_client, rated_team):
    fx = rated_team
    resp = await async_client.get(
        f"{BASE}/teams/999999999/peer-ratings", headers=fx["owner_headers"],
    )
    assert resp.status_code == 404
