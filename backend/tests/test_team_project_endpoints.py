"""Regression tests for the Team Projects feature as actually shipped
(app/api/v1/endpoints/team_project.py + services), covering bugs found
while reviewing it — not a full spec-compliance suite (the shipped
implementation is a simpler design than the original 7-phase spec; see
session notes). Each test below maps to one fix:

1. GET /team-projects/my used to fetch the ENTIRE team_projects table and
   return every other team's member skill levels + task scores/feedback/
   submission URLs to any student in the same project — a real data leak,
   not just a missing feature. Fixed by scoping the query to the student's
   own team projects and redacting every other team in the response.
2. POST .../finalize had no guard against being called twice — a second
   call created a duplicate Project and silently overwrote
   final_project_id. Fixed with a status check + row lock.
3. POST .../reassign had NO ownership check at all — any teacher account
   could reassign any task on any team platform-wide. Fixed to match
   regenerate's existing check.
4. review_task_submission graded against the bare submission_url/
   submission_files STRING, never the actual code — fixed to fetch real
   content via github_repo_service, same as ai_review_service.py's main
   pipeline.
"""
import json
import uuid
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from sqlalchemy import select

from app.models.group import Group, student_groups
from app.models.team_project import (
    TeamProject, TeamProjectTeam, TeamProjectMember, TeamProjectTask,
    TeamRole, TeamStatus, TaskStatus,
)
from app.models.user import Student
from app.services.team_project_service import create_team_project
from app.services.team_project_task_review import review_task_submission

BASE = "/api/v1/team-projects"


async def _register(async_client, prefix: str) -> tuple[int, str]:
    """Returns (id, username) — the actual registered username includes
    this helper's own random suffix, so a caller that needs to log in
    later must use the returned username, not reconstruct one itself."""
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
async def two_teams_project(async_client, db_session):
    """1 teacher, 4 students (forms into 2 teams of 2 via create_team_project,
    team_size=2), with the AI planner patched to a no-op so team formation
    is deterministic and doesn't depend on any real AI call."""
    uid = uuid.uuid4().hex[:8]

    teacher_reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": f"tpt_{uid}", "email": f"tpt_{uid}@example.com", "password": "pass12345"},
    )
    assert teacher_reg.status_code == 201
    teacher_id = teacher_reg.json()["user"]["id"]
    teacher_username = f"tpt_{uid}"

    student_ids = []
    student_usernames = []
    for i in range(4):
        sid, sname = await _register(async_client, f"tps_{uid}_{i}")
        student_ids.append(sid)
        student_usernames.append(sname)

    teacher = (await db_session.execute(select(Student).where(Student.id == teacher_id))).scalar_one()
    teacher.role = "teacher"
    group = Group(name="TP Endpoint Group", teacher_id=teacher_id)
    db_session.add(group)
    await db_session.flush()
    for sid in student_ids:
        await db_session.execute(student_groups.insert().values(student_id=sid, group_id=group.id))
    await db_session.commit()

    # side_effect closes the coroutine instead of just swallowing it, so
    # Python doesn't warn "coroutine was never awaited" at GC time.
    with patch(
        "app.services.team_project_service.spawn_background_task",
        side_effect=lambda coro: coro.close(),
    ):
        tp = await create_team_project(
            db_session, group_id=group.id, course_id=None, teacher_id=teacher_id,
            team_size=2, deadline_days=14,
        )
    await db_session.commit()

    teams = (await db_session.execute(
        select(TeamProjectTeam).where(TeamProjectTeam.team_project_id == tp.id)
    )).scalars().all()
    assert len(teams) == 2, "fixture assumes 4 students / team_size=2 -> exactly 2 teams"

    teacher_headers = await _login_headers(async_client, teacher_username)
    student_headers = {
        uname: await _login_headers(async_client, uname)
        for uname in student_usernames
    }

    return {
        "teacher_id": teacher_id, "teacher_headers": teacher_headers,
        "team_project_id": tp.id, "teams": teams,
        "student_ids": student_ids, "student_usernames": student_usernames,
        "student_headers": student_headers, "group_id": group.id,
    }


async def _member_usernames_for_team(db_session, team_id, fixture) -> list[str]:
    members = (await db_session.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team_id)
    )).scalars().all()
    id_to_username = dict(zip(fixture["student_ids"], fixture["student_usernames"]))
    return [id_to_username[m.student_id] for m in members]


# ── 1. /my no longer leaks other teams' skill data ─────────────────────────

async def test_my_team_projects_redacts_other_teams_skill_levels(
    async_client, db_session, two_teams_project,
):
    fx = two_teams_project
    team_a, team_b = fx["teams"]
    members_a = await _member_usernames_for_team(db_session, team_a.id, fx)
    headers = fx["student_headers"][members_a[0]]

    resp = await async_client.get(f"{BASE}/my", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    entry = data[0]

    teams_in_response = entry["team_project"]["teams"]
    assert len(teams_in_response) == 2
    my_team_in_list = next(t for t in teams_in_response if t["id"] == team_a.id)
    other_team_in_list = next(t for t in teams_in_response if t["id"] == team_b.id)

    # My own team: full detail, real levels.
    assert all(m["level_at_assignment"] for m in my_team_in_list["members"])
    # The OTHER team: redacted — no skill levels, no tasks.
    assert all(m["level_at_assignment"] == "" for m in other_team_in_list["members"])
    assert other_team_in_list["tasks"] == []
    # my_team (the dedicated field) is still the full, unredacted version.
    assert entry["my_team"]["id"] == team_a.id
    assert all(m["level_at_assignment"] for m in entry["my_team"]["members"])


async def test_my_team_projects_only_returns_projects_the_student_belongs_to(
    async_client, db_session, two_teams_project,
):
    """Also guards the N+1/platform-wide-scan bug alongside the leak: a
    student with zero team-project membership anywhere must get an empty
    list, not every team project on the platform."""
    uid = uuid.uuid4().hex[:8]
    username = f"outsider_{uid}"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "pass12345"},
    )
    assert reg.status_code == 201
    headers = await _login_headers(async_client, username)

    resp = await async_client.get(f"{BASE}/my", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


# ── 2. GET /{id} is teacher-only now ─────────────────────────────────────────

async def test_get_assignment_rejects_students(async_client, two_teams_project):
    fx = two_teams_project
    any_student_headers = next(iter(fx["student_headers"].values()))
    resp = await async_client.get(f"{BASE}/{fx['team_project_id']}", headers=any_student_headers)
    assert resp.status_code == 403


async def test_get_assignment_rejects_other_teachers(async_client, two_teams_project):
    other_teacher_id, _ = await _register(async_client, "otherteacher")
    from app.db.database import AsyncSessionLocal
    async with AsyncSessionLocal() as s:
        t = (await s.execute(select(Student).where(Student.id == other_teacher_id))).scalar_one()
        t.role = "teacher"
        other_username = t.username
        await s.commit()
    other_headers = await _login_headers(async_client, other_username)

    fx = two_teams_project
    resp = await async_client.get(f"{BASE}/{fx['team_project_id']}", headers=other_headers)
    assert resp.status_code == 403


async def test_get_assignment_allows_the_owning_teacher(async_client, two_teams_project):
    fx = two_teams_project
    resp = await async_client.get(f"{BASE}/{fx['team_project_id']}", headers=fx["teacher_headers"])
    assert resp.status_code == 200
    assert len(resp.json()["teams"]) == 2


# ── 2b. submit_task doesn't crash on response serialization ────────────────

async def test_submit_task_succeeds_without_crashing(async_client, db_session, two_teams_project):
    """Regression test for a real MissingGreenlet 500: _task_read accesses
    task.assigned_student, which db.refresh(task) (no attribute_names)
    doesn't reload — the first uncached access outside an async-aware load
    crashed every real call to this endpoint. Found via this exact test,
    not a pre-existing report."""
    fx = two_teams_project
    team_a = fx["teams"][0]
    members_a = (await db_session.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team_a.id)
    )).scalars().all()
    task = TeamProjectTask(
        team_id=team_a.id, assigned_student_id=members_a[0].student_id, order=1,
        title="T", title_ru="Т", description="D", description_ru="О",
        required_level="Beginner", interface_contract_json="{}",
        acceptance_criteria_json="[]", depends_on_json="[]", estimated_hours=4,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    submitter_id = members_a[0].student_id
    submitter_username = next(
        u for sid, u in zip(fx["student_ids"], fx["student_usernames"]) if sid == submitter_id
    )

    with patch(
        "app.api.v1.endpoints.team_project.review_task_submission",
        new=AsyncMock(return_value={"success": False, "reason": "skipped in test"}),
    ):
        resp = await async_client.post(
            f"{BASE}/teams/{team_a.id}/tasks/{task.id}/submit",
            json={"submission_url": "https://github.com/acme/repo"},
            headers=fx["student_headers"][submitter_username],
        )
    assert resp.status_code == 200, resp.text
    assert resp.json()["submission_url"] == "https://github.com/acme/repo"


# ── 3. reassign_task ownership check ────────────────────────────────────────

async def test_reassign_task_rejects_non_owning_teacher(async_client, db_session, two_teams_project):
    fx = two_teams_project
    team_a = fx["teams"][0]
    task = TeamProjectTask(
        team_id=team_a.id, assigned_student_id=fx["student_ids"][0], order=1,
        title="T", title_ru="Т", description="D", description_ru="О",
        required_level="Beginner", interface_contract_json="{}",
        acceptance_criteria_json="[]", depends_on_json="[]", estimated_hours=4,
    )
    db_session.add(task)
    await db_session.commit()

    other_teacher_id, _ = await _register(async_client, "reassignintruder")
    from app.db.database import AsyncSessionLocal
    async with AsyncSessionLocal() as s:
        t = (await s.execute(select(Student).where(Student.id == other_teacher_id))).scalar_one()
        t.role = "teacher"
        other_username = t.username
        await s.commit()
    other_headers = await _login_headers(async_client, other_username)

    resp = await async_client.post(
        f"{BASE}/teams/{team_a.id}/tasks/{task.id}/reassign",
        json={"student_id": fx["student_ids"][1]},
        headers=other_headers,
    )
    assert resp.status_code == 403


async def test_reassign_task_allows_owning_teacher(async_client, db_session, two_teams_project):
    fx = two_teams_project
    team_a = fx["teams"][0]
    members_a = (await db_session.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team_a.id)
    )).scalars().all()
    task = TeamProjectTask(
        team_id=team_a.id, assigned_student_id=members_a[0].student_id, order=1,
        title="T", title_ru="Т", description="D", description_ru="О",
        required_level="Beginner", interface_contract_json="{}",
        acceptance_criteria_json="[]", depends_on_json="[]", estimated_hours=4,
    )
    db_session.add(task)
    await db_session.commit()

    resp = await async_client.post(
        f"{BASE}/teams/{team_a.id}/tasks/{task.id}/reassign",
        json={"student_id": members_a[1].student_id},
        headers=fx["teacher_headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["assigned_student_id"] == members_a[1].student_id
    assert resp.json()["status"] == "assigned"


# ── 4. finalize idempotency ─────────────────────────────────────────────────

async def test_finalize_twice_returns_409_not_a_duplicate_project(
    async_client, db_session, two_teams_project,
):
    fx = two_teams_project
    team_a = fx["teams"][0]
    members_a = (await db_session.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team_a.id)
    )).scalars().all()
    lead_id = team_a.lead_student_id
    lead_username = next(
        u for sid, u in zip(fx["student_ids"], fx["student_usernames"]) if sid == lead_id
    )
    lead_headers = fx["student_headers"][lead_username]

    task = TeamProjectTask(
        team_id=team_a.id, assigned_student_id=members_a[0].student_id, order=1,
        title="T", title_ru="Т", description="D", description_ru="О",
        required_level="Beginner", interface_contract_json="{}",
        acceptance_criteria_json="[]", depends_on_json="[]", estimated_hours=4,
        status=TaskStatus.approved,
    )
    db_session.add(task)
    await db_session.commit()

    from app.models.project import Project
    # Scoped to this lead's own projects — the shared test DB accumulates
    # Project rows across the whole suite, so a bare unscoped count isn't
    # meaningful here (this is about this test's own delta, not the total).
    count_for_lead = lambda: db_session.execute(
        select(Project).where(Project.student_id == lead_id)
    )

    first = await async_client.post(
        f"{BASE}/teams/{team_a.id}/finalize",
        json={"github_url": "https://github.com/acme/repo1"},
        headers=lead_headers,
    )
    assert first.status_code == 200, first.text
    assert len((await count_for_lead()).scalars().all()) == 1

    second = await async_client.post(
        f"{BASE}/teams/{team_a.id}/finalize",
        json={"github_url": "https://github.com/acme/repo2"},
        headers=lead_headers,
    )
    assert second.status_code == 409

    assert len((await count_for_lead()).scalars().all()) == 1, (
        "finalize-twice must not create a second Project"
    )


async def test_finalize_rejects_non_lead(async_client, db_session, two_teams_project):
    fx = two_teams_project
    team_a = fx["teams"][0]
    members_a = (await db_session.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team_a.id)
    )).scalars().all()
    non_lead_id = next(m.student_id for m in members_a if m.student_id != team_a.lead_student_id)
    non_lead_username = next(
        u for sid, u in zip(fx["student_ids"], fx["student_usernames"]) if sid == non_lead_id
    )
    resp = await async_client.post(
        f"{BASE}/teams/{team_a.id}/finalize",
        json={"github_url": "https://github.com/acme/repo"},
        headers=fx["student_headers"][non_lead_username],
    )
    assert resp.status_code == 403


# ── 5. task review fetches real code, not just the URL string ──────────────

async def test_review_task_submission_fetches_real_repo_content(db_session, two_teams_project):
    fx = two_teams_project
    team_a = fx["teams"][0]
    members_a = (await db_session.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team_a.id)
    )).scalars().all()
    task = TeamProjectTask(
        team_id=team_a.id, assigned_student_id=members_a[0].student_id, order=1,
        title="T", title_ru="Т", description="D", description_ru="О",
        required_level="Beginner", interface_contract_json="{}",
        acceptance_criteria_json="[]", depends_on_json="[]", estimated_hours=4,
        status=TaskStatus.submitted, submission_url="https://github.com/acme/repo",
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    fake_snapshot = {
        "exists": True, "content_text": "=== FILE: index.js ===\nconsole.log('hi');",
        "error": None, "files_included": ["index.js"],
    }
    ai_response = {
        "score": 85, "approved": True, "criteria_results": [], "contract_violations": [],
        "feedback": "yaxshi", "feedback_ru": "хорошо",
    }
    with patch(
        "app.services.team_project_task_review.fetch_github_snapshot",
        new=AsyncMock(return_value=fake_snapshot),
    ) as mock_fetch, patch(
        "app.services.team_project_task_review.call_chain",
        new=AsyncMock(return_value=(json.dumps(ai_response), ai_response, "groq", [])),
    ) as mock_call_chain:
        result = await review_task_submission(db_session, task.id)

    assert result["success"] is True
    mock_fetch.assert_called_once_with("https://github.com/acme/repo")
    # The actual code content must have reached the prompt — not just the URL.
    prompt_sent = mock_call_chain.call_args[0][0]
    assert "console.log('hi')" in prompt_sent

    await db_session.refresh(task)
    assert task.status == TaskStatus.approved
    assert task.ai_score == 85


async def test_review_task_submission_penalizes_unfetchable_repo(db_session, two_teams_project):
    fx = two_teams_project
    team_a = fx["teams"][0]
    members_a = (await db_session.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team_a.id)
    )).scalars().all()
    task = TeamProjectTask(
        team_id=team_a.id, assigned_student_id=members_a[0].student_id, order=1,
        title="T", title_ru="Т", description="D", description_ru="О",
        required_level="Beginner", interface_contract_json="{}",
        acceptance_criteria_json="[]", depends_on_json="[]", estimated_hours=4,
        status=TaskStatus.submitted, submission_url="https://github.com/acme/private-or-missing",
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    empty_snapshot = {"exists": False, "content_text": "", "error": "404 not found"}
    captured_prompt = {}

    async def _fake_call_chain(prompt, max_tokens, validator=None):
        captured_prompt["value"] = prompt
        resp = {"score": 20, "approved": False, "criteria_results": [], "contract_violations": [],
                "feedback": "kod yuklanmagan", "feedback_ru": "код не загружен"}
        return json.dumps(resp), resp, "groq", []

    with patch(
        "app.services.team_project_task_review.fetch_github_snapshot",
        new=AsyncMock(return_value=empty_snapshot),
    ), patch(
        "app.services.team_project_task_review.call_chain",
        new=_fake_call_chain,
    ):
        result = await review_task_submission(db_session, task.id)

    assert result["success"] is True
    assert "o'qib bo'lmadi" in captured_prompt["value"]
    assert "404 not found" in captured_prompt["value"]
