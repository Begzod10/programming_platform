"""Tests for GET /teams/{team_id}/events (app/api/v1/endpoints/
team_project.py) — closes the last gap flagged by a full feature audit:
TeamProjectEvent is an append-only audit log every state change in this
feature already writes to (team formation, AI plan generation, reassign,
finalize, points, task review), but nothing ever read it back — a
write-only audit trail nobody could audit.
"""
import json
import uuid

import pytest_asyncio
from sqlalchemy import select

from app.models.group import Group, student_groups
from app.models.team_project import TeamProject, TeamProjectTeam, TeamProjectEvent
from app.models.user import Student

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


async def _login_headers(async_client, username: str) -> dict:
    login = await async_client.post(
        "/api/v1/auth/login", json={"username": username, "password": "pass12345"},
    )
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest_asyncio.fixture
async def team_with_events(async_client, db_session):
    """1 owning teacher, 1 other teacher, 1 student, a team with 2 events
    already recorded (one system-originated, one actor-attributed)."""
    uid = uuid.uuid4().hex[:8]

    owner_id, owner_username = await _register(async_client, f"tev_owner_{uid}")
    other_teacher_id, other_teacher_username = await _register(async_client, f"tev_other_{uid}")
    student_id, student_username = await _register(async_client, f"tev_s_{uid}")

    for tid in (owner_id, other_teacher_id):
        t = (await db_session.execute(select(Student).where(Student.id == tid))).scalar_one()
        t.role = "teacher"

    group = Group(name="Events Group", teacher_id=owner_id)
    db_session.add(group)
    await db_session.flush()
    await db_session.execute(student_groups.insert().values(student_id=student_id, group_id=group.id))

    team_project = TeamProject(group_id=group.id, teacher_id=owner_id, team_size=2, deadline_days=14)
    db_session.add(team_project)
    await db_session.flush()
    team = TeamProjectTeam(team_project_id=team_project.id, name="Team 1")
    db_session.add(team)
    await db_session.flush()

    db_session.add(TeamProjectEvent(
        team_project_id=team_project.id, team_id=team.id,
        event_type="team_formed",
        payload_json=json.dumps({"member_ids": [student_id], "theme": "crm"}),
    ))
    db_session.add(TeamProjectEvent(
        team_project_id=team_project.id, team_id=team.id,
        actor_student_id=student_id, event_type="team_finalized",
        payload_json=json.dumps({"final_project_id": 42}),
    ))
    await db_session.commit()

    return {
        "team_id": team.id,
        "owner_headers": await _login_headers(async_client, owner_username),
        "other_teacher_headers": await _login_headers(async_client, other_teacher_username),
        "student_headers": await _login_headers(async_client, student_username),
        "student_id": student_id, "student_username": student_username,
    }


async def test_owning_teacher_sees_events_newest_first_with_resolved_actor(async_client, team_with_events):
    fx = team_with_events
    resp = await async_client.get(f"{BASE}/teams/{fx['team_id']}/events", headers=fx["owner_headers"])
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 2

    # Newest first: team_finalized (2nd write) before team_formed (1st write).
    assert data[0]["event_type"] == "team_finalized"
    assert data[0]["actor_student_id"] == fx["student_id"]
    assert data[0]["actor_name"] == fx["student_username"]
    assert data[0]["payload"] == {"final_project_id": 42}

    assert data[1]["event_type"] == "team_formed"
    assert data[1]["actor_student_id"] is None
    assert data[1]["actor_name"] is None
    assert data[1]["payload"] == {"member_ids": [fx["student_id"]], "theme": "crm"}


async def test_non_owning_teacher_is_rejected(async_client, team_with_events):
    fx = team_with_events
    resp = await async_client.get(f"{BASE}/teams/{fx['team_id']}/events", headers=fx["other_teacher_headers"])
    assert resp.status_code == 403


async def test_student_cannot_view_the_endpoint_at_all(async_client, team_with_events):
    fx = team_with_events
    resp = await async_client.get(f"{BASE}/teams/{fx['team_id']}/events", headers=fx["student_headers"])
    assert resp.status_code in (401, 403)


async def test_unknown_team_returns_404(async_client, team_with_events):
    fx = team_with_events
    resp = await async_client.get(f"{BASE}/teams/999999999/events", headers=fx["owner_headers"])
    assert resp.status_code == 404
