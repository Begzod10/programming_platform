"""Tests for POST /team-projects/teams/{team_id}/manual-plan — the
teacher-authored fallback for when AI planning isn't usable (no provider
configured, or /regenerate already burned all MAX_GENERATION_ATTEMPTS).
Before this endpoint, a team stuck in `forming` with no working AI plan
had no way forward at all.
"""
import uuid

import pytest_asyncio
from sqlalchemy import select

from app.models.group import Group, student_groups
from app.models.team_project import (
    TeamProject, TeamProjectTeam, TeamProjectMember, TeamProjectTask, TeamStatus,
)
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
async def forming_team(async_client, db_session):
    """A team of 2 students in `forming` status, no tasks/plan yet — the
    exact state a team is left in when AI generation was never attempted
    (no provider configured) or has exhausted its attempts."""
    uid = uuid.uuid4().hex[:8]

    student_ids, usernames = [], []
    for i in range(2):
        sid, uname = await _register(async_client, f"mpts_{uid}_{i}")
        student_ids.append(sid)
        usernames.append(uname)

    teacher_id, teacher_uname = await _register(async_client, f"mpt_{uid}")
    teacher = (await db_session.execute(select(Student).where(Student.id == teacher_id))).scalar_one()
    teacher.role = "teacher"
    group = Group(name="Manual Plan Group", teacher_id=teacher_id)
    db_session.add(group)
    await db_session.flush()
    for sid in student_ids:
        await db_session.execute(student_groups.insert().values(student_id=sid, group_id=group.id))

    tp = TeamProject(group_id=group.id, teacher_id=teacher_id, status="active")
    db_session.add(tp)
    await db_session.flush()
    team = TeamProjectTeam(team_project_id=tp.id, name="Team 1")
    db_session.add(team)
    await db_session.flush()
    for sid in student_ids:
        db_session.add(TeamProjectMember(
            team_id=team.id, student_id=sid, role="member",
            level_at_assignment="Beginner", skill_summary_at_assignment="x",
        ))
    await db_session.commit()

    teacher_headers = await _login_headers(async_client, teacher_uname)
    return {
        "teacher_headers": teacher_headers, "teacher_id": teacher_id,
        "team_id": team.id, "student_ids": student_ids,
    }


def _valid_tasks(student_ids):
    return [
        {
            "assigned_student_id": student_ids[0],
            "title": "Login form", "title_ru": "Login formasi",
            "description": "d", "description_ru": "o",
            "required_level": "Beginner",
            "interface_contract": {"produces": ["POST /api/login -> {token}"], "consumes": []},
            "acceptance_criteria": ["works"],
            "depends_on": [],
            "estimated_hours": 4,
        },
        {
            "assigned_student_id": student_ids[1],
            "title": "Dashboard", "title_ru": "Boshqaruv paneli",
            "description": "d", "description_ru": "o",
            "required_level": "Beginner",
            "interface_contract": {"produces": [], "consumes": ["POST /api/login -> {token}"]},
            "acceptance_criteria": ["works"],
            "depends_on": [0],
            "estimated_hours": 4,
        },
    ]


async def test_manual_plan_creates_tasks_and_moves_team_to_working(async_client, db_session, forming_team):
    fx = forming_team
    resp = await async_client.post(
        f"{BASE}/teams/{fx['team_id']}/manual-plan",
        headers=fx["teacher_headers"],
        json={"project_title": "Mini CRM", "project_description": "d",
              "tasks": _valid_tasks(fx["student_ids"])},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "working"
    assert body["project_title"] == "Mini CRM"
    assert len(body["tasks"]) == 2

    team = (await db_session.execute(
        select(TeamProjectTeam).where(TeamProjectTeam.id == fx["team_id"])
    )).scalar_one()
    assert team.status == TeamStatus.working
    assert team.ai_plan_json is None  # no AI plan for a manually-authored one


async def test_manual_plan_rejects_cyclic_dependency(async_client, forming_team):
    fx = forming_team
    tasks = _valid_tasks(fx["student_ids"])
    tasks[0]["depends_on"] = [1]  # 0 <-> 1 cycle
    resp = await async_client.post(
        f"{BASE}/teams/{fx['team_id']}/manual-plan",
        headers=fx["teacher_headers"],
        json={"project_title": "x", "tasks": tasks},
    )
    assert resp.status_code == 400
    assert "cycle" in resp.json()["error"]["message"]


async def test_manual_plan_rejects_level_above_assigned_member(async_client, forming_team):
    fx = forming_team
    tasks = _valid_tasks(fx["student_ids"])
    tasks[0]["required_level"] = "Advanced"  # member is Beginner
    resp = await async_client.post(
        f"{BASE}/teams/{fx['team_id']}/manual-plan",
        headers=fx["teacher_headers"],
        json={"project_title": "x", "tasks": tasks},
    )
    assert resp.status_code == 400
    assert "exceeds member" in resp.json()["error"]["message"]


async def test_manual_plan_rejects_non_member_assignee(async_client, forming_team):
    fx = forming_team
    tasks = _valid_tasks(fx["student_ids"])
    tasks[0]["assigned_student_id"] = 999999
    resp = await async_client.post(
        f"{BASE}/teams/{fx['team_id']}/manual-plan",
        headers=fx["teacher_headers"],
        json={"project_title": "x", "tasks": tasks},
    )
    assert resp.status_code == 400
    assert "bu jamoa a'zosi emas" in resp.json()["error"]["message"]


async def test_manual_plan_rejects_when_team_already_has_a_plan(async_client, db_session, forming_team):
    fx = forming_team
    ok = await async_client.post(
        f"{BASE}/teams/{fx['team_id']}/manual-plan",
        headers=fx["teacher_headers"],
        json={"project_title": "Mini CRM", "tasks": _valid_tasks(fx["student_ids"])},
    )
    assert ok.status_code == 200

    again = await async_client.post(
        f"{BASE}/teams/{fx['team_id']}/manual-plan",
        headers=fx["teacher_headers"],
        json={"project_title": "Another", "tasks": _valid_tasks(fx["student_ids"])},
    )
    assert again.status_code == 400


async def test_manual_plan_requires_teacher_ownership(async_client, db_session, forming_team):
    fx = forming_team
    other_teacher_id, other_uname = await _register(async_client, "other_teacher")
    other_teacher = (await db_session.execute(
        select(Student).where(Student.id == other_teacher_id)
    )).scalar_one()
    other_teacher.role = "teacher"
    await db_session.commit()
    other_headers = await _login_headers(async_client, other_uname)

    resp = await async_client.post(
        f"{BASE}/teams/{fx['team_id']}/manual-plan",
        headers=other_headers,
        json={"project_title": "x", "tasks": _valid_tasks(fx["student_ids"])},
    )
    assert resp.status_code == 403

