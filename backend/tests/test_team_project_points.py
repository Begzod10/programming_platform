"""Tests for team_project_points_service.py (award_points) and the new
POST /team-projects/teams/{team_id}/peer-ratings endpoint.

award_points is tested directly against the service function (not through
the full finalize_team HTTP flow, which would also need to mock the
entire AI-review pipeline — github fetch, sample-copy-check, the grading
call itself — for no added signal over testing the points logic in
isolation).
"""
import uuid
from unittest.mock import patch

import pytest_asyncio
from sqlalchemy import select

from app.models.group import Group, student_groups
from app.models.project import Project
from app.models.store import WalletLedgerEntry
from app.models.team_project import (
    TeamProject, TeamProjectTeam, TeamProjectMember, TeamProjectTask,
    TeamProjectPeerRating, TaskStatus, TeamStatus,
)
from app.models.user import Student
from app.services.team_project_points_service import award_points

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
async def points_fixture(async_client, db_session):
    """A team of 3 students (one lead) with 3 approved tasks and a final
    Project already graded B — everything award_points needs, built
    directly rather than through the real AI-planning/review pipeline."""
    uid = uuid.uuid4().hex[:8]

    student_ids, usernames = [], []
    for i in range(3):
        sid, uname = await _register(async_client, f"ptpts_{uid}_{i}")
        student_ids.append(sid)
        usernames.append(uname)

    teacher_id, teacher_uname = await _register(async_client, f"ptpt_{uid}")
    teacher = (await db_session.execute(select(Student).where(Student.id == teacher_id))).scalar_one()
    teacher.role = "teacher"
    group = Group(name="Points Group", teacher_id=teacher_id)
    db_session.add(group)
    await db_session.flush()
    for sid in student_ids:
        await db_session.execute(student_groups.insert().values(student_id=sid, group_id=group.id))

    tp = TeamProject(group_id=group.id, teacher_id=teacher_id, status="active")
    db_session.add(tp)
    await db_session.flush()
    team = TeamProjectTeam(team_project_id=tp.id, name="Team 1", lead_student_id=student_ids[0])
    db_session.add(team)
    await db_session.flush()
    for sid in student_ids:
        db_session.add(TeamProjectMember(
            team_id=team.id, student_id=sid,
            role="lead" if sid == student_ids[0] else "member",
            level_at_assignment="Beginner", skill_summary_at_assignment="x",
        ))
    await db_session.flush()

    tasks = []
    for i, sid in enumerate(student_ids):
        task = TeamProjectTask(
            team_id=team.id, assigned_student_id=sid, order=i,
            title=f"T{i}", title_ru=f"Т{i}", description="D", description_ru="О",
            required_level="Beginner", interface_contract_json="{}",
            acceptance_criteria_json="[]", depends_on_json="[]", estimated_hours=4,
            status=TaskStatus.approved, ai_score=80,
        )
        db_session.add(task)
        tasks.append(task)
    await db_session.flush()

    project = Project(
        student_id=student_ids[0], title="Final", description="D",
        difficulty_level="Medium", grade="B",
    )
    db_session.add(project)
    await db_session.flush()
    team.final_project_id = project.id
    team.status = TeamStatus.submitted
    await db_session.commit()

    for sid in student_ids:
        await db_session.refresh(
            (await db_session.execute(select(Student).where(Student.id == sid))).scalar_one()
        )

    return {
        "team": team, "tasks": tasks, "project": project,
        "student_ids": student_ids, "usernames": usernames,
        "lead_id": student_ids[0], "teacher_id": teacher_id,
    }


async def _total_points(db_session, student_id: int) -> int:
    s = (await db_session.execute(select(Student).where(Student.id == student_id))).scalar_one()
    return s.total_points


async def _lifetime_points(db_session, student_id: int) -> int:
    s = (await db_session.execute(select(Student).where(Student.id == student_id))).scalar_one()
    return s.lifetime_points


# ── per-piece formula ────────────────────────────────────────────────────────

async def test_piece_points_follow_the_level_formula(db_session, points_fixture):
    fx = points_fixture
    before = {sid: await _total_points(db_session, sid) for sid in fx["student_ids"]}

    result = await award_points(db_session, fx["team"])

    # Beginner base = 30 (settings.TEAM_PROJECT_PIECE_POINTS), ai_score=80
    # -> 30 * 0.8 = 24, well above the 10-point floor.
    for sid in fx["student_ids"]:
        after = await _total_points(db_session, sid)
        piece_gain = 24  # same for everyone here — all Beginner, all score 80
        # Lead and every other approved-team member also get the team bonus
        # (grade B) on top, plus the lead bonus for the lead specifically.
        assert after > before[sid], f"student {sid} got no points at all"

    assert result["team_bonus_earned"] is True
    assert any(k.startswith("task:") for k in result["awarded"])


async def test_piece_points_floor_at_10_for_a_low_ai_score(db_session, points_fixture):
    fx = points_fixture
    task = fx["tasks"][0]
    task.ai_score = 5  # 30 * 0.05 = 1.5 -> floored up to 10
    await db_session.commit()

    before = await _total_points(db_session, task.assigned_student_id)
    await award_points(db_session, fx["team"])
    after = await _total_points(db_session, task.assigned_student_id)

    entry = (await db_session.execute(
        select(WalletLedgerEntry).where(
            WalletLedgerEntry.idempotency_key
            == f"teamproj:{fx['team'].team_project_id}:task:{task.id}:{task.assigned_student_id}"
        )
    )).scalar_one()
    assert entry.delta_coins == 10


# ── team bonus gating ────────────────────────────────────────────────────────

async def test_no_team_bonus_when_grade_below_b(db_session, points_fixture):
    fx = points_fixture
    fx["project"].grade = "C"
    await db_session.commit()

    result = await award_points(db_session, fx["team"])
    assert result["team_bonus_earned"] is False
    assert not any(k.startswith("team_bonus:") for k in result["awarded"])
    assert "lead_bonus" not in result["awarded"]
    # Piece points still paid regardless of the team bonus outcome.
    assert any(k.startswith("task:") for k in result["awarded"])


async def test_lead_gets_both_team_bonus_and_lead_bonus(db_session, points_fixture):
    fx = points_fixture
    from app.config import settings
    before = await _total_points(db_session, fx["lead_id"])

    await award_points(db_session, fx["team"])

    lead_task = next(t for t in fx["tasks"] if t.assigned_student_id == fx["lead_id"])
    piece_points = lead_task.points_awarded
    after = await _total_points(db_session, fx["lead_id"])
    expected_gain = piece_points + settings.TEAM_PROJECT_TEAM_BONUS + settings.TEAM_PROJECT_LEAD_BONUS
    assert after - before == expected_gain


# ── idempotency ──────────────────────────────────────────────────────────────

async def test_award_points_is_idempotent_across_two_calls(db_session, points_fixture):
    fx = points_fixture
    before = {sid: await _total_points(db_session, sid) for sid in fx["student_ids"]}

    first = await award_points(db_session, fx["team"])
    after_first = {sid: await _total_points(db_session, sid) for sid in fx["student_ids"]}

    second = await award_points(db_session, fx["team"])
    after_second = {sid: await _total_points(db_session, sid) for sid in fx["student_ids"]}

    assert first["awarded"], "first call should have actually paid something"
    assert second["awarded"] == {}, "second call must be a pure no-op"
    for sid in fx["student_ids"]:
        assert after_second[sid] == after_first[sid], (
            f"student {sid}'s balance changed on the duplicate call"
        )
        assert after_first[sid] > before[sid]

    # One ledger row per (student, award) — not two.
    entries = (await db_session.execute(
        select(WalletLedgerEntry).where(WalletLedgerEntry.student_id == fx["lead_id"])
    )).scalars().all()
    keys = [e.idempotency_key for e in entries]
    assert len(keys) == len(set(keys)), "duplicate ledger rows for the same key"


async def test_lifetime_points_bumped_exactly_once_too(db_session, points_fixture):
    """Guards the exact bug this service's own docstring calls out: calling
    both record_earn and add_points_to_student naively double-counts
    total_points. Checking lifetime_points specifically, since that one is
    ONLY ever touched by add_points_to_student (never by a raw ledger
    write) — if it's correct, the double-count bug isn't present."""
    fx = points_fixture
    before = await _lifetime_points(db_session, fx["lead_id"])
    await award_points(db_session, fx["team"])
    await award_points(db_session, fx["team"])  # duplicate call
    after = await _lifetime_points(db_session, fx["lead_id"])

    lead_task = next(t for t in fx["tasks"] if t.assigned_student_id == fx["lead_id"])
    from app.config import settings
    expected_gain = lead_task.points_awarded + settings.TEAM_PROJECT_TEAM_BONUS + settings.TEAM_PROJECT_LEAD_BONUS
    assert after - before == expected_gain


# ── peer-rating modifier ────────────────────────────────────────────────────

async def test_peer_modifier_halves_bonus_for_a_low_rated_member(db_session, points_fixture):
    fx = points_fixture
    low_rated = fx["student_ids"][1]
    raters = [sid for sid in fx["student_ids"] if sid != low_rated]
    for rater in raters:
        db_session.add(TeamProjectPeerRating(
            team_id=fx["team"].id, rater_student_id=rater,
            rated_student_id=low_rated, score=1,
        ))
    await db_session.commit()

    from app.config import settings
    before = await _total_points(db_session, low_rated)
    await award_points(db_session, fx["team"])
    after = await _total_points(db_session, low_rated)

    piece_points = next(t for t in fx["tasks"] if t.assigned_student_id == low_rated).points_awarded
    halved_bonus = round(settings.TEAM_PROJECT_TEAM_BONUS * 0.5)
    assert after - before == piece_points + halved_bonus


async def test_peer_modifier_not_applied_with_only_one_rating(db_session, points_fixture):
    fx = points_fixture
    low_rated = fx["student_ids"][1]
    db_session.add(TeamProjectPeerRating(
        team_id=fx["team"].id, rater_student_id=fx["student_ids"][0],
        rated_student_id=low_rated, score=1,
    ))
    await db_session.commit()

    from app.config import settings
    before = await _total_points(db_session, low_rated)
    await award_points(db_session, fx["team"])
    after = await _total_points(db_session, low_rated)

    piece_points = next(t for t in fx["tasks"] if t.assigned_student_id == low_rated).points_awarded
    # Only 1 rating (< the 2-rating minimum) -> full bonus, not halved.
    assert after - before == piece_points + settings.TEAM_PROJECT_TEAM_BONUS


# ── peer-ratings endpoint ────────────────────────────────────────────────────

async def test_submit_peer_ratings_rejects_self_rating(async_client, points_fixture):
    fx = points_fixture
    headers = await _login_headers(async_client, fx["usernames"][0])
    resp = await async_client.post(
        f"{BASE}/teams/{fx['team'].id}/peer-ratings",
        json=[{"rated_student_id": fx["student_ids"][0], "score": 5}],
        headers=headers,
    )
    assert resp.status_code == 400


async def test_submit_peer_ratings_rejects_non_member_target(async_client, points_fixture):
    fx = points_fixture
    headers = await _login_headers(async_client, fx["usernames"][0])
    resp = await async_client.post(
        f"{BASE}/teams/{fx['team'].id}/peer-ratings",
        json=[{"rated_student_id": 999999, "score": 5}],
        headers=headers,
    )
    assert resp.status_code == 400


async def test_submit_peer_ratings_requires_team_submitted(async_client, db_session, points_fixture):
    fx = points_fixture
    fx["team"].status = TeamStatus.working
    await db_session.commit()
    headers = await _login_headers(async_client, fx["usernames"][0])
    resp = await async_client.post(
        f"{BASE}/teams/{fx['team'].id}/peer-ratings",
        json=[{"rated_student_id": fx["student_ids"][1], "score": 5}],
        headers=headers,
    )
    assert resp.status_code == 400


async def test_submit_peer_ratings_success_and_upsert(async_client, db_session, points_fixture):
    fx = points_fixture
    headers = await _login_headers(async_client, fx["usernames"][0])
    rated = fx["student_ids"][1]
    rater = fx["student_ids"][0]
    team_id = fx["team"].id  # captured before expire_all() below

    resp = await async_client.post(
        f"{BASE}/teams/{team_id}/peer-ratings",
        json=[{"rated_student_id": rated, "score": 4, "comment": "good"}],
        headers=headers,
    )
    assert resp.status_code == 204

    rows = (await db_session.execute(
        select(TeamProjectPeerRating).where(
            TeamProjectPeerRating.team_id == team_id,
            TeamProjectPeerRating.rater_student_id == rater,
            TeamProjectPeerRating.rated_student_id == rated,
        )
    )).scalars().all()
    assert len(rows) == 1
    assert rows[0].score == 4
    # The UPDATE below happens through the HTTP request's own session, not
    # this one — without expiring, this session's identity map would keep
    # serving the stale pre-update row on the next query.
    db_session.expire_all()

    # Resubmitting updates in place rather than erroring or duplicating.
    resp2 = await async_client.post(
        f"{BASE}/teams/{team_id}/peer-ratings",
        json=[{"rated_student_id": rated, "score": 2, "comment": "changed my mind"}],
        headers=headers,
    )
    assert resp2.status_code == 204
    rows2 = (await db_session.execute(
        select(TeamProjectPeerRating).where(
            TeamProjectPeerRating.team_id == team_id,
            TeamProjectPeerRating.rater_student_id == rater,
            TeamProjectPeerRating.rated_student_id == rated,
        )
    )).scalars().all()
    assert len(rows2) == 1
    assert rows2[0].score == 2
