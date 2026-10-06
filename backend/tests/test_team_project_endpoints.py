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
5. POST .../regenerate had no guard against two overlapping requests for
   the same team (confirmed live on a real assignment: a teacher
   double-clicking while the AI call was slow left 4 tasks instead of 2,
   and burned 2 of 3 generation_attempts on what felt like one click).
   Fixed the same way as finalize (#2): a row lock via with_for_update.
"""
import asyncio
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
            team_size=2, deadline_days=14, student_ids=student_ids,
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


# ── 3b. regenerate concurrency guard ────────────────────────────────────────

async def test_concurrent_regenerate_does_not_duplicate_tasks(
    async_client, db_session, two_teams_project,
):
    """Regression test for a real production incident (team 1 of
    assignment #1, "Onlayn do'kon", 2026-09-12): two /regenerate requests
    for the same team, 15s apart — a teacher double-clicking while the AI
    call was still in flight — each read the same pre-race task set,
    deleted it, and generated an independent plan, leaving 4 tasks instead
    of 2 and burning 2 of the team's 3 generation_attempts on what the
    teacher experienced as one click.

    Fired here via asyncio.gather (each request gets its own DB session —
    see app/db/session.py's get_db, not shared with the db_session
    fixture), with an artificial delay patched into the AI call so both
    requests' coroutines genuinely interleave on the event loop the way
    two real overlapping HTTP requests would.
    """
    fx = two_teams_project
    team = fx["teams"][0]
    members = (await db_session.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team.id)
    )).scalars().all()
    assert len(members) == 2, "fixture assumes team_size=2"

    def _plan_for(label: str) -> dict:
        return {
            "project_title": f"Loyiha {label}",
            "project_description": "desc",
            "tasks": [
                {
                    "title": f"Task {label} {i}", "title_ru": f"Задача {label} {i}",
                    # Detailed enough to clear validate_plan's content-quality
                    # floor (MIN_DESCRIPTION_LEN/MIN_ACCEPTANCE_CRITERIA/
                    # bilingual checks).
                    "description": f"Build task {label} {i} with a form and validation logic.",
                    "description_ru": f"Постройте задачу {label} {i} с формой и логикой валидации.",
                    "required_level": "Beginner", "assign_to_member_index": i,
                    "interface_contract": {"files": [f"src/Task{i}.jsx"], "produces": [], "consumes": []},
                    "acceptance_criteria": ["First concrete criterion", "Second concrete criterion"],
                    "acceptance_criteria_ru": ["Первый конкретный критерий", "Второй конкретный критерий"],
                    "depends_on": [], "estimated_hours": 4,
                }
                for i in range(2)
            ],
        }

    call_count = 0

    async def _fake_call_chain(prompt, max_tokens=2000, validator=None):
        nonlocal call_count
        call_count += 1
        label = f"L{call_count}"
        # Yields control so both concurrent requests' coroutines actually
        # interleave, the way two overlapping real HTTP requests would
        # while an AI provider call is in flight.
        await asyncio.sleep(0.05)
        return "raw", _plan_for(label), "mock-provider", 1

    with patch("app.services.team_project_planner.call_chain", new=_fake_call_chain):
        results = await asyncio.gather(
            async_client.post(f"{BASE}/teams/{team.id}/regenerate", headers=fx["teacher_headers"]),
            async_client.post(f"{BASE}/teams/{team.id}/regenerate", headers=fx["teacher_headers"]),
        )

    for r in results:
        assert r.status_code == 200, r.text

    tasks = (await db_session.execute(
        select(TeamProjectTask).where(TeamProjectTask.team_id == team.id)
    )).scalars().all()
    assert len(tasks) == len(members), (
        f"expected exactly {len(members)} tasks after 2 concurrent regenerates, "
        f"got {len(tasks)} -- a duplicate-plan race"
    )


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


# ── audit fixes: regenerate guard, failed-regenerate recovery, no duplicate plan ──

def _plain_task(team_id, student_id, status=TaskStatus.assigned):
    return TeamProjectTask(
        team_id=team_id, assigned_student_id=student_id, order=0,
        title="T", title_ru="Т", description="D", description_ru="О",
        required_level="Beginner", interface_contract_json="{}",
        acceptance_criteria_json="[]", depends_on_json="[]", estimated_hours=4,
        status=status,
    )


async def test_regenerate_is_rejected_on_a_finalized_team(async_client, db_session, two_teams_project):
    fx = two_teams_project
    team = fx["teams"][0]
    member = (await db_session.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team.id)
    )).scalars().first()
    team.status = TeamStatus.reviewed
    db_session.add(_plain_task(team.id, member.student_id, TaskStatus.approved))
    await db_session.commit()

    resp = await async_client.post(f"{BASE}/teams/{team.id}/regenerate", headers=fx["teacher_headers"])
    assert resp.status_code == 400, resp.text

    remaining = (await db_session.execute(
        select(TeamProjectTask).where(TeamProjectTask.team_id == team.id)
    )).scalars().all()
    assert len(remaining) == 1, "a finalized team's approved work must not be wiped"


async def test_failed_regenerate_returns_team_to_forming_not_stranded_working(
    async_client, db_session, two_teams_project,
):
    fx = two_teams_project
    team = fx["teams"][0]
    member = (await db_session.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team.id)
    )).scalars().first()
    team.status = TeamStatus.working
    db_session.add(_plain_task(team.id, member.student_id))
    await db_session.commit()

    async def _ai_down(*args, **kwargs):
        raise RuntimeError("provider down")

    with patch("app.services.team_project_planner.call_chain", new=_ai_down):
        resp = await async_client.post(f"{BASE}/teams/{team.id}/regenerate", headers=fx["teacher_headers"])
    assert resp.status_code == 200, resp.text

    await db_session.refresh(team)
    assert team.status == TeamStatus.forming  # manual-plan fallback only accepts "forming"
    left = (await db_session.execute(
        select(TeamProjectTask).where(TeamProjectTask.team_id == team.id)
    )).scalars().all()
    assert left == []


async def test_generate_plan_skips_a_team_that_already_has_tasks(db_session, two_teams_project):
    from unittest.mock import AsyncMock
    from app.services.team_project_planner import generate_plan_for_team

    fx = two_teams_project
    team = fx["teams"][0]
    member = (await db_session.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team.id)
    )).scalars().first()
    db_session.add(_plain_task(team.id, member.student_id))
    await db_session.commit()
    attempts_before = team.generation_attempts

    ai = AsyncMock()
    with patch("app.services.team_project_planner.call_chain", new=ai):
        await generate_plan_for_team(db_session, team.id)

    ai.assert_not_awaited()
    await db_session.refresh(team)
    assert team.generation_attempts == attempts_before


async def test_reassign_is_rejected_for_an_approved_task(async_client, db_session, two_teams_project):
    fx = two_teams_project
    team = fx["teams"][0]
    members = (await db_session.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team.id)
    )).scalars().all()
    task = _plain_task(team.id, members[0].student_id, TaskStatus.approved)
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    resp = await async_client.post(
        f"{BASE}/teams/{team.id}/tasks/{task.id}/reassign",
        headers=fx["teacher_headers"], json={"student_id": members[1].student_id},
    )
    assert resp.status_code == 400, resp.text


# ── teacher verdict, deadline enforcement/extension, stale review, dependency cleanup ──

async def _other_teacher_headers(async_client) -> dict:
    other_teacher_id, _ = await _register(async_client, "otherteacher")
    from app.db.database import AsyncSessionLocal
    async with AsyncSessionLocal() as s:
        t = (await s.execute(select(Student).where(Student.id == other_teacher_id))).scalar_one()
        t.role = "teacher"
        other_username = t.username
        await s.commit()
    return await _login_headers(async_client, other_username)


async def _team_with_task(db_session, fx, status=TaskStatus.submitted, **task_kwargs):
    team = fx["teams"][0]
    members = (await db_session.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team.id)
    )).scalars().all()
    team.status = TeamStatus.working
    task = _plain_task(team.id, members[0].student_id, status)
    for k, v in task_kwargs.items():
        setattr(task, k, v)
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    username = next(u for sid, u in zip(fx["student_ids"], fx["student_usernames"])
                    if sid == members[0].student_id)
    return team, task, fx["student_headers"][username]


async def test_teacher_can_approve_a_submitted_task(async_client, db_session, two_teams_project):
    fx = two_teams_project
    team, task, _ = await _team_with_task(db_session, fx)
    resp = await async_client.post(
        f"{BASE}/teams/{team.id}/tasks/{task.id}/teacher-review",
        headers=fx["teacher_headers"], json={"decision": "approve", "comment": "Zo'r"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "approved"
    assert resp.json()["lead_comment"] == "Zo'r"


async def test_teacher_request_changes_needs_a_comment(async_client, db_session, two_teams_project):
    fx = two_teams_project
    team, task, _ = await _team_with_task(db_session, fx)
    url = f"{BASE}/teams/{team.id}/tasks/{task.id}/teacher-review"
    bad = await async_client.post(url, headers=fx["teacher_headers"], json={"decision": "request_changes"})
    assert bad.status_code == 400
    ok = await async_client.post(
        url, headers=fx["teacher_headers"], json={"decision": "request_changes", "comment": "Login ishlamaydi"})
    assert ok.status_code == 200 and ok.json()["status"] == "changes_requested"


async def test_teacher_review_rejects_other_teachers_students_and_bad_states(
    async_client, db_session, two_teams_project,
):
    fx = two_teams_project
    team, task, student_headers = await _team_with_task(db_session, fx)
    url = f"{BASE}/teams/{team.id}/tasks/{task.id}/teacher-review"
    body = {"decision": "approve"}
    assert (await async_client.post(url, headers=student_headers, json=body)).status_code == 403
    assert (await async_client.post(url, headers=await _other_teacher_headers(async_client), json=body)).status_code == 403

    task.status = TaskStatus.assigned  # never submitted
    await db_session.commit()
    assert (await async_client.post(url, headers=fx["teacher_headers"], json=body)).status_code == 400

    task.status = TaskStatus.approved  # already final
    await db_session.commit()
    assert (await async_client.post(url, headers=fx["teacher_headers"], json=body)).status_code == 400


async def test_submit_after_deadline_is_rejected_until_teacher_extends(
    async_client, db_session, two_teams_project,
):
    from datetime import timedelta
    from app.utils.datetime_utils import utcnow
    fx = two_teams_project
    team, task, student_headers = await _team_with_task(
        db_session, fx, status=TaskStatus.assigned, deadline_at=utcnow() - timedelta(days=1))
    submit_url = f"{BASE}/teams/{team.id}/tasks/{task.id}/submit"
    payload = {"submission_url": "https://github.com/acme/repo"}
    review = AsyncMock(return_value={"success": False, "reason": "skipped"})

    with patch("app.api.v1.endpoints.team_project.review_task_submission", new=review):
        late = await async_client.post(submit_url, json=payload, headers=student_headers)
        assert late.status_code == 400, late.text

        ext = await async_client.post(
            f"{BASE}/teams/{team.id}/extend-deadline", json={"days": 3}, headers=fx["teacher_headers"])
        assert ext.status_code == 200 and ext.json()["extended_tasks"] == 1

        ok = await async_client.post(submit_url, json=payload, headers=student_headers)
        assert ok.status_code == 200, ok.text


async def test_extend_deadline_rejects_other_teachers_and_bad_days(
    async_client, db_session, two_teams_project,
):
    fx = two_teams_project
    team, _, _ = await _team_with_task(db_session, fx)
    url = f"{BASE}/teams/{team.id}/extend-deadline"
    assert (await async_client.post(url, json={"days": 3}, headers=await _other_teacher_headers(async_client))).status_code == 403
    assert (await async_client.post(url, json={"days": 0}, headers=fx["teacher_headers"])).status_code == 422


async def test_stale_ai_review_does_not_overwrite_a_teacher_verdict(db_session, two_teams_project):
    """The AI call is slow; if the teacher decides meanwhile, the late AI
    result must be dropped, not clobber the verdict."""
    from app.services import team_project_task_review as module
    fx = two_teams_project
    team, task, _ = await _team_with_task(
        db_session, fx, status=TaskStatus.submitted, submission_url="https://github.com/acme/repo")

    async def _slow_ai(*args, **kwargs):
        task.status = TaskStatus.approved          # teacher approves during the AI call
        task.lead_comment = "teacher said so"
        await db_session.commit()
        return "raw", {"score": 20, "approved": False}, "mock", 1

    with patch.object(module, "fetch_github_snapshot",
                      new=AsyncMock(return_value={"exists": True, "content_text": "x"})), \
         patch.object(module, "call_chain", new=_slow_ai):
        result = await review_task_submission(db_session, task.id)

    assert result["success"] is False
    await db_session.refresh(task)
    assert task.status == TaskStatus.approved and task.lead_comment == "teacher said so"


async def test_deleting_a_task_removes_it_from_siblings_depends_on(
    async_client, db_session, two_teams_project,
):
    import json as _json
    fx = two_teams_project
    team = fx["teams"][0]
    members = (await db_session.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team.id)
    )).scalars().all()
    team.status = TeamStatus.working
    first = _plain_task(team.id, members[0].student_id)
    second = _plain_task(team.id, members[1].student_id)
    second.order = 1
    second.depends_on_json = _json.dumps([0])
    db_session.add_all([first, second])
    await db_session.commit()
    await db_session.refresh(first)
    await db_session.refresh(second)

    resp = await async_client.delete(
        f"{BASE}/teams/{team.id}/tasks/{first.id}", headers=fx["teacher_headers"])
    assert resp.status_code == 204, resp.text
    await db_session.refresh(second)
    assert _json.loads(second.depends_on_json) == []


# ── plan generation: auto-repair + one AI repair round ──

def _generated_plan(member_count, *, broken=False):
    tasks = [
        {
            "title": f"Task {i}", "title_ru": f"Задача {i}",
            "description": f"Build task number {i} with a form and validation logic.",
            "description_ru": f"Постройте задачу номер {i} с формой и логикой валидации.",
            "required_level": "Beginner", "assign_to_member_index": i,
            "interface_contract": {"files": [f"src/Task{i}.jsx"], "produces": [], "consumes": []},
            "acceptance_criteria": ["First concrete criterion", "Second concrete criterion"],
            "acceptance_criteria_ru": ["Первый конкретный критерий", "Второй конкретный критерий"],
            "depends_on": [], "estimated_hours": 4,
        }
        for i in range(member_count)
    ]
    if broken:
        tasks.pop()   # wrong task count: not something deterministic repair can fix
    return {"project_title": "Loyiha", "project_description": "desc", "tasks": tasks}


async def _fresh_team(db_session, fx):
    team = fx["teams"][0]
    members = (await db_session.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team.id)
    )).scalars().all()
    return team, len(members)


async def test_generation_with_a_wrong_task_count_is_repaired_by_a_second_ai_call(
    db_session, two_teams_project,
):
    from app.services.team_project_planner import generate_plan_for_team
    fx = two_teams_project
    team, n = await _fresh_team(db_session, fx)
    calls = []

    async def _ai(prompt, max_tokens=2000, validator=None):
        calls.append(prompt)
        return "raw", _generated_plan(n, broken=len(calls) == 1), "mock", 1

    with patch("app.services.team_project_planner.call_chain", new=_ai):
        await generate_plan_for_team(db_session, team.id)

    assert len(calls) == 2
    assert "XATOLAR" in calls[1] and "Expected" in calls[1]     # the errors were shown to the model
    await db_session.refresh(team)
    assert team.generation_attempts == 1                          # one attempt, not two
    tasks = (await db_session.execute(
        select(TeamProjectTask).where(TeamProjectTask.team_id == team.id))).scalars().all()
    assert len(tasks) == n


async def test_valid_first_response_makes_a_single_ai_call(db_session, two_teams_project):
    from app.services.team_project_planner import generate_plan_for_team
    fx = two_teams_project
    team, n = await _fresh_team(db_session, fx)
    ai = AsyncMock(return_value=("raw", _generated_plan(n), "mock", 1))
    with patch("app.services.team_project_planner.call_chain", new=ai):
        await generate_plan_for_team(db_session, team.id)
    assert ai.await_count == 1


async def test_still_invalid_after_the_repair_round_fails_and_returns_team_to_forming(
    db_session, two_teams_project,
):
    from app.services.team_project_planner import generate_plan_for_team
    fx = two_teams_project
    team, n = await _fresh_team(db_session, fx)
    ai = AsyncMock(return_value=("raw", _generated_plan(n, broken=True), "mock", 1))
    with patch("app.services.team_project_planner.call_chain", new=ai):
        await generate_plan_for_team(db_session, team.id)
    assert ai.await_count == 2
    await db_session.refresh(team)
    assert team.status == TeamStatus.forming and team.generation_attempts == 1


async def test_regenerate_refreshes_the_members_skill_summary(
    async_client, db_session, two_teams_project,
):
    fx = two_teams_project
    team, n = await _fresh_team(db_session, fx)
    members = (await db_session.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team.id))).scalars().all()
    for m in members:
        m.skill_summary_at_assignment = "STALE snapshot"
    await db_session.commit()

    ai = AsyncMock(return_value=("raw", _generated_plan(n), "mock", 1))
    with patch("app.services.team_project_planner.call_chain", new=ai):
        resp = await async_client.post(f"{BASE}/teams/{team.id}/regenerate", headers=fx["teacher_headers"])
    assert resp.status_code == 200, resp.text

    await db_session.refresh(members[0])
    assert members[0].skill_summary_at_assignment != "STALE snapshot"
    assert "STALE snapshot" not in ai.await_args.args[0]       # the model saw the fresh one
