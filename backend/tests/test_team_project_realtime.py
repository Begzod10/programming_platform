"""Tests for Team Projects realtime updates (WebSocket broadcast on state
change) — team_project.py's team_ws/team_project_ws endpoints +
broadcast_team/broadcast_project helpers, and app/ws/manager.py's
ConnectionManager itself (previously untested, despite already running in
production for the team-game feature).

No test here opens a real WebSocket connection — this codebase's own
existing WS feature (team_game_session.py) has no such test either (only
route-registration checks, see test_team_game_session_split.py), so this
matches that established level of rigor rather than introducing new test
infrastructure. Broadcast correctness is verified by patching the
ConnectionManager instances' .broadcast method and asserting call shape.
"""
import uuid
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.main import app
from app.models.group import Group, student_groups
from app.models.team_project import (
    TeamProject, TeamProjectTeam, TeamProjectMember, TeamProjectTask,
    TeamRole, TeamStatus, TaskStatus,
)
from app.models.user import Student
from app.ws.manager import ConnectionManager

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
async def team_with_task(async_client, db_session):
    """1 teacher, 2 students, 1 working team with 1 task assigned+unsubmitted
    to student 0 (the lead)."""
    uid = uuid.uuid4().hex[:8]

    student_ids, usernames = [], []
    for i in range(2):
        sid, uname = await _register(async_client, f"rts_{uid}_{i}")
        student_ids.append(sid)
        usernames.append(uname)

    teacher_id, teacher_uname = await _register(async_client, f"rtt_{uid}")
    teacher = (await db_session.execute(select(Student).where(Student.id == teacher_id))).scalar_one()
    teacher.role = "teacher"
    group = Group(name="Realtime Group", teacher_id=teacher_id)
    db_session.add(group)
    await db_session.flush()
    for sid in student_ids:
        await db_session.execute(student_groups.insert().values(student_id=sid, group_id=group.id))

    tp = TeamProject(group_id=group.id, teacher_id=teacher_id, status="active")
    db_session.add(tp)
    await db_session.flush()
    team = TeamProjectTeam(
        team_project_id=tp.id, name="Team 1", status=TeamStatus.working,
        lead_student_id=student_ids[0],
    )
    db_session.add(team)
    await db_session.flush()
    for i, sid in enumerate(student_ids):
        db_session.add(TeamProjectMember(
            team_id=team.id, student_id=sid,
            role=TeamRole.lead if i == 0 else TeamRole.member,
            level_at_assignment="Beginner", skill_summary_at_assignment="x",
        ))
    task = TeamProjectTask(
        team_id=team.id, assigned_student_id=student_ids[0], order=0,
        title="T", title_ru="Т", description="D", description_ru="О",
        required_level="Beginner", interface_contract_json="{}",
        acceptance_criteria_json="[]", depends_on_json="[]", estimated_hours=4,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    teacher_headers = await _login_headers(async_client, teacher_uname)
    student_headers = [await _login_headers(async_client, u) for u in usernames]

    return {
        "teacher_id": teacher_id, "teacher_headers": teacher_headers,
        "team_project_id": tp.id, "team_id": team.id, "task_id": task.id,
        "student_ids": student_ids, "student_headers": student_headers,
    }


# ── Route registration ──────────────────────────────────────────────────────

def test_realtime_ws_routes_are_registered():
    ws_paths = {
        getattr(r, "path", None) for r in app.routes
        if "WebSocketRoute" in type(r).__name__
    }
    assert "/api/v1/team-projects/teams/{team_id}/ws" in ws_paths
    assert "/api/v1/team-projects/{team_project_id}/ws" in ws_paths


# ── ConnectionManager (previously untested) ─────────────────────────────────

class _FakeWebSocket:
    def __init__(self, fail=False):
        self.accepted = False
        self.sent = []
        self.fail = fail

    async def accept(self):
        self.accepted = True

    async def send_json(self, payload):
        if self.fail:
            raise RuntimeError("connection dropped")
        self.sent.append(payload)


async def test_connection_manager_broadcasts_to_all_connected_sockets():
    manager = ConnectionManager()
    ws1, ws2 = _FakeWebSocket(), _FakeWebSocket()
    await manager.connect(1, ws1)
    await manager.connect(1, ws2)
    await manager.broadcast(1, {"type": "x"})
    assert ws1.sent == [{"type": "x"}]
    assert ws2.sent == [{"type": "x"}]


async def test_connection_manager_only_broadcasts_to_the_matching_id():
    manager = ConnectionManager()
    ws_a, ws_b = _FakeWebSocket(), _FakeWebSocket()
    await manager.connect(1, ws_a)
    await manager.connect(2, ws_b)
    await manager.broadcast(1, {"type": "x"})
    assert ws_a.sent == [{"type": "x"}]
    assert ws_b.sent == []


async def test_connection_manager_disconnect_removes_socket():
    manager = ConnectionManager()
    ws = _FakeWebSocket()
    await manager.connect(1, ws)
    manager.disconnect(1, ws)
    await manager.broadcast(1, {"type": "x"})
    assert ws.sent == []


async def test_connection_manager_drops_dead_sockets_without_raising():
    manager = ConnectionManager()
    dead, alive = _FakeWebSocket(fail=True), _FakeWebSocket()
    await manager.connect(1, dead)
    await manager.connect(1, alive)
    await manager.broadcast(1, {"type": "x"})  # must not raise despite `dead` failing
    assert alive.sent == [{"type": "x"}]
    # the dead socket should have been dropped by the failed send
    await manager.broadcast(1, {"type": "y"})
    assert alive.sent == [{"type": "x"}, {"type": "y"}]


# ── broadcast_team / broadcast_project ──────────────────────────────────────

async def test_broadcast_team_sends_correct_shape(db_session, team_with_task):
    from app.api.v1.endpoints.team_project import broadcast_team
    fx = team_with_task
    with patch("app.api.v1.endpoints.team_project.team_ws_manager.broadcast", new=AsyncMock()) as mock_broadcast:
        await broadcast_team(db_session, fx["team_id"])
    mock_broadcast.assert_awaited_once()
    sent_id, payload = mock_broadcast.await_args.args
    assert sent_id == fx["team_id"]
    assert payload["type"] == "team_update"
    assert payload["data"]["id"] == fx["team_id"]
    assert payload["data"]["status"] == "working"
    assert len(payload["data"]["tasks"]) == 1


async def test_broadcast_project_sends_correct_shape(db_session, team_with_task):
    from app.api.v1.endpoints.team_project import broadcast_project
    fx = team_with_task
    with patch("app.api.v1.endpoints.team_project.team_project_ws_manager.broadcast", new=AsyncMock()) as mock_broadcast:
        await broadcast_project(db_session, fx["team_project_id"])
    mock_broadcast.assert_awaited_once()
    sent_id, payload = mock_broadcast.await_args.args
    assert sent_id == fx["team_project_id"]
    assert payload["type"] == "project_update"
    assert payload["data"]["id"] == fx["team_project_id"]
    assert len(payload["data"]["teams"]) == 1


async def test_broadcast_team_noop_for_missing_team(db_session):
    from app.api.v1.endpoints.team_project import broadcast_team
    with patch("app.api.v1.endpoints.team_project.team_ws_manager.broadcast", new=AsyncMock()) as mock_broadcast:
        await broadcast_team(db_session, 999999)
    mock_broadcast.assert_not_awaited()


async def test_broadcast_project_noop_for_missing_project(db_session):
    from app.api.v1.endpoints.team_project import broadcast_project
    with patch("app.api.v1.endpoints.team_project.team_project_ws_manager.broadcast", new=AsyncMock()) as mock_broadcast:
        await broadcast_project(db_session, 999999)
    mock_broadcast.assert_not_awaited()


# ── Endpoint wiring: each mutation actually triggers a broadcast ───────────

@pytest.fixture
def _patched_managers():
    with patch("app.api.v1.endpoints.team_project.team_ws_manager.broadcast", new=AsyncMock()) as team_mock, \
         patch("app.api.v1.endpoints.team_project.team_project_ws_manager.broadcast", new=AsyncMock()) as project_mock:
        yield team_mock, project_mock


async def test_submit_task_triggers_broadcast(async_client, team_with_task, _patched_managers):
    fx = team_with_task
    team_mock, project_mock = _patched_managers
    resp = await async_client.post(
        f"{BASE}/teams/{fx['team_id']}/tasks/{fx['task_id']}/submit",
        headers=fx["student_headers"][0],
        json={"submission_url": "https://github.com/example/repo"},
    )
    assert resp.status_code == 200, resp.text
    assert team_mock.await_args.args[0] == fx["team_id"]
    assert project_mock.await_args.args[0] == fx["team_project_id"]


async def test_reassign_task_triggers_broadcast(async_client, team_with_task, _patched_managers):
    fx = team_with_task
    team_mock, project_mock = _patched_managers
    resp = await async_client.post(
        f"{BASE}/teams/{fx['team_id']}/tasks/{fx['task_id']}/reassign",
        headers=fx["teacher_headers"],
        json={"student_id": fx["student_ids"][1]},
    )
    assert resp.status_code == 200, resp.text
    assert team_mock.await_args.args[0] == fx["team_id"]
    assert project_mock.await_args.args[0] == fx["team_project_id"]


async def test_finalize_triggers_broadcast(async_client, db_session, team_with_task, _patched_managers):
    fx = team_with_task
    team_mock, project_mock = _patched_managers
    task = (await db_session.execute(
        select(TeamProjectTask).where(TeamProjectTask.id == fx["task_id"])
    )).scalar_one()
    task.status = TaskStatus.approved
    await db_session.commit()

    resp = await async_client.post(
        f"{BASE}/teams/{fx['team_id']}/finalize",
        headers=fx["student_headers"][0],
        json={"github_url": "https://github.com/example/final"},
    )
    assert resp.status_code == 200, resp.text
    assert team_mock.await_args.args[0] == fx["team_id"]
    assert project_mock.await_args.args[0] == fx["team_project_id"]


async def test_manual_plan_triggers_broadcast(async_client, db_session, _patched_managers):
    team_mock, project_mock = _patched_managers
    uid = uuid.uuid4().hex[:8]
    sid, sname = await _register(async_client, f"mprt_{uid}")
    teacher_id, teacher_uname = await _register(async_client, f"mprt_t_{uid}")
    teacher = (await db_session.execute(select(Student).where(Student.id == teacher_id))).scalar_one()
    teacher.role = "teacher"
    group = Group(name="Manual RT Group", teacher_id=teacher_id)
    db_session.add(group)
    await db_session.flush()
    await db_session.execute(student_groups.insert().values(student_id=sid, group_id=group.id))
    tp = TeamProject(group_id=group.id, teacher_id=teacher_id, status="active")
    db_session.add(tp)
    await db_session.flush()
    team = TeamProjectTeam(team_project_id=tp.id, name="Team 1")
    db_session.add(team)
    await db_session.flush()
    db_session.add(TeamProjectMember(
        team_id=team.id, student_id=sid, role=TeamRole.member,
        level_at_assignment="Beginner", skill_summary_at_assignment="x",
    ))
    await db_session.commit()
    teacher_headers = await _login_headers(async_client, teacher_uname)

    resp = await async_client.post(
        f"{BASE}/teams/{team.id}/manual-plan",
        headers=teacher_headers,
        json={
            "project_title": "Mini CRM",
            "tasks": [{
                "assigned_student_id": sid,
                "title": "T", "title_ru": "Т", "description": "D", "description_ru": "О",
                "required_level": "Beginner",
                "interface_contract": {"produces": [], "consumes": []},
                "acceptance_criteria": [], "depends_on": [], "estimated_hours": 4,
            }],
        },
    )
    assert resp.status_code == 200, resp.text
    assert team_mock.await_args.args[0] == team.id
    assert project_mock.await_args.args[0] == tp.id


# ── generate_plan_for_team: the one place with no request/response cycle ───
# to piggyback a broadcast on at all — it only ever runs from a background
# task, so without this a student watching a still-`forming` team has no
# way to find out generation finished (or failed) short of reload-polling.

async def _forming_team_for_planner(async_client, db_session, uid):
    sid, sname = await _register(async_client, f"plrt_{uid}")
    teacher_id, teacher_uname = await _register(async_client, f"plrt_t_{uid}")
    teacher = (await db_session.execute(select(Student).where(Student.id == teacher_id))).scalar_one()
    teacher.role = "teacher"
    group = Group(name="Planner RT Group", teacher_id=teacher_id)
    db_session.add(group)
    await db_session.flush()
    await db_session.execute(student_groups.insert().values(student_id=sid, group_id=group.id))
    tp = TeamProject(group_id=group.id, teacher_id=teacher_id, status="active")
    db_session.add(tp)
    await db_session.flush()
    team = TeamProjectTeam(team_project_id=tp.id, name="Team 1", theme="crm", tech_stack="react")
    db_session.add(team)
    await db_session.flush()
    db_session.add(TeamProjectMember(
        team_id=team.id, student_id=sid, role=TeamRole.member,
        level_at_assignment="Beginner", skill_summary_at_assignment="x",
    ))
    await db_session.commit()
    return team.id, tp.id


async def test_generate_plan_for_team_broadcasts_on_success(async_client, db_session):
    from app.services.team_project_planner import generate_plan_for_team
    team_id, tp_id = await _forming_team_for_planner(async_client, db_session, uuid.uuid4().hex[:8])

    valid_plan = {
        "project_title": "Mini CRM", "project_description": "d",
        "tasks": [{
            "assign_to_member_index": 0, "title": "T", "title_ru": "Т",
            "description": "D", "description_ru": "О", "required_level": "Beginner",
            "interface_contract": {"produces": [], "consumes": []},
            "acceptance_criteria": ["ok"], "depends_on": [], "estimated_hours": 4,
        }],
    }
    with patch(
        "app.services.team_project_planner.call_chain",
        new=AsyncMock(return_value=("...", valid_plan, "openai", [])),
    ), patch(
        "app.api.v1.endpoints.team_project.team_ws_manager.broadcast", new=AsyncMock(),
    ) as team_mock, patch(
        "app.api.v1.endpoints.team_project.team_project_ws_manager.broadcast", new=AsyncMock(),
    ) as project_mock:
        await generate_plan_for_team(db_session, team_id)

    assert team_mock.await_args.args[0] == team_id
    assert project_mock.await_args.args[0] == tp_id


async def test_generate_plan_for_team_broadcasts_on_failure(async_client, db_session):
    from app.services.team_project_planner import generate_plan_for_team
    team_id, tp_id = await _forming_team_for_planner(async_client, db_session, uuid.uuid4().hex[:8])

    with patch(
        "app.services.team_project_planner.call_chain",
        new=AsyncMock(side_effect=RuntimeError("no providers configured")),
    ), patch(
        "app.api.v1.endpoints.team_project.team_ws_manager.broadcast", new=AsyncMock(),
    ) as team_mock, patch(
        "app.api.v1.endpoints.team_project.team_project_ws_manager.broadcast", new=AsyncMock(),
    ) as project_mock:
        await generate_plan_for_team(db_session, team_id)

    assert team_mock.await_args.args[0] == team_id
    assert project_mock.await_args.args[0] == tp_id
