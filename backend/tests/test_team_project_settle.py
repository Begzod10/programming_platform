"""Team project points settlement:

1. A final Project whose review failed at finalize (AI down, private repo)
   used to leave the team "submitted" with no points for good. Now the lead
   can finalize again after a review-less rejection (same Project row), a
   private repo is refused up front, and job_settle_team_projects pays a team
   whose review landed later.
2. The team bonus carries the peer-rating modifier, but ratings open only
   after finalize, so paying it in the finalize request always saw zero
   ratings. It now waits until every member has rated (or 48 hours).
"""
from datetime import timedelta
from unittest.mock import AsyncMock, patch

from sqlalchemy import select

from app.config import settings
from app.models.project import Project
from app.models.team_project import TeamProjectPeerRating, TeamProjectTeam, TeamStatus
from app.services.team_project_points_service import award_points, peer_ratings_complete
from app.utils.datetime_utils import utcnow
from app.models.store import LedgerReason, WalletLedgerEntry
from tests.test_team_project_points import (
    BASE, _login_headers,
    points_fixture, two_person_points_fixture,  # noqa: F401  (pytest fixtures)
)


async def _total_points(db_session, student_id: int) -> int:
    """Team-project points only (the ledger rows award_points writes);
    achievements unlocked on the way add points of their own."""
    rows = (await db_session.execute(
        select(WalletLedgerEntry.delta_coins).where(
            WalletLedgerEntry.student_id == student_id,
            WalletLedgerEntry.reason == LedgerReason.earn_team_project,
        )
    )).scalars().all()
    return sum(rows)


def _piece(fx, student_id):
    task = next(t for t in fx["tasks"] if t.assigned_student_id == student_id)
    # Beginner level, ai_score=80 — same formula as _piece_points.
    base = settings.TEAM_PROJECT_PIECE_POINTS["Beginner"]
    return max(10, round(base * task.ai_score / 100))


async def _mark_reviewed(db_session, fx, *, submitted_ago=timedelta(0)):
    fx["project"].reviewed_at = utcnow()
    fx["team"].submitted_at = utcnow() - submitted_ago
    await db_session.commit()


async def _settle(db_session, team):
    from app.api.v1.endpoints.team_project import settle_team_points
    return await settle_team_points(db_session, team)


# ── award_points without the team bonus ─────────────────────────────────────

async def test_award_points_can_hold_back_the_team_bonus(db_session, points_fixture):
    fx = points_fixture
    lead, member = fx["lead_id"], fx["student_ids"][1]
    before_lead = await _total_points(db_session, lead)
    before_member = await _total_points(db_session, member)

    await award_points(db_session, fx["team"], include_team_bonus=False)

    assert await _total_points(db_session, lead) - before_lead == _piece(fx, lead) + settings.TEAM_PROJECT_LEAD_BONUS
    assert await _total_points(db_session, member) - before_member == _piece(fx, member)


async def test_peer_ratings_complete_needs_every_pair(db_session, two_person_points_fixture):
    fx = two_person_points_fixture
    a, b = fx["student_ids"]
    assert not await peer_ratings_complete(db_session, fx["team"].id, [a, b])
    db_session.add(TeamProjectPeerRating(team_id=fx["team"].id, rater_student_id=a, rated_student_id=b, score=4))
    await db_session.commit()
    assert not await peer_ratings_complete(db_session, fx["team"].id, [a, b])
    db_session.add(TeamProjectPeerRating(team_id=fx["team"].id, rater_student_id=b, rated_student_id=a, score=4))
    await db_session.commit()
    assert await peer_ratings_complete(db_session, fx["team"].id, [a, b])


# ── settle_team_points ──────────────────────────────────────────────────────

async def test_settle_does_nothing_before_the_final_review(db_session, points_fixture):
    fx = points_fixture
    before = await _total_points(db_session, fx["lead_id"])
    assert await _settle(db_session, fx["team"]) is False
    await db_session.refresh(fx["team"])
    assert fx["team"].status == TeamStatus.submitted
    assert await _total_points(db_session, fx["lead_id"]) == before


async def test_team_bonus_waits_for_ratings_and_then_applies_the_penalty(db_session, points_fixture):
    fx = points_fixture
    await _mark_reviewed(db_session, fx)
    low = fx["student_ids"][1]
    others = [s for s in fx["student_ids"] if s != low]
    start = {s: await _total_points(db_session, s) for s in fx["student_ids"]}

    assert await _settle(db_session, fx["team"]) is True
    await db_session.refresh(fx["team"])
    assert fx["team"].status == TeamStatus.reviewed
    assert await _total_points(db_session, low) - start[low] == _piece(fx, low)

    # Every member rates every teammate; `low` gets 1 star from both.
    for rater in fx["student_ids"]:
        for rated in fx["student_ids"]:
            if rater != rated:
                db_session.add(TeamProjectPeerRating(
                    team_id=fx["team"].id, rater_student_id=rater, rated_student_id=rated,
                    score=1 if rated == low else 5,
                ))
    await db_session.commit()
    await _settle(db_session, fx["team"])

    assert await _total_points(db_session, low) - start[low] == (
        _piece(fx, low) + round(settings.TEAM_PROJECT_TEAM_BONUS * 0.5)
    )
    for s in others:
        extra = settings.TEAM_PROJECT_LEAD_BONUS if s == fx["lead_id"] else 0
        assert await _total_points(db_session, s) - start[s] == (
            _piece(fx, s) + settings.TEAM_PROJECT_TEAM_BONUS + extra
        )


async def test_team_bonus_is_paid_in_full_after_the_grace_period(db_session, points_fixture):
    fx = points_fixture
    await _mark_reviewed(db_session, fx, submitted_ago=timedelta(hours=49))
    member = fx["student_ids"][1]
    before = await _total_points(db_session, member)

    await _settle(db_session, fx["team"])
    await _settle(db_session, fx["team"])  # idempotent

    assert await _total_points(db_session, member) - before == _piece(fx, member) + settings.TEAM_PROJECT_TEAM_BONUS


async def test_last_peer_rating_through_the_endpoint_pays_the_bonus(
    async_client, db_session, two_person_points_fixture,
):
    fx = two_person_points_fixture
    await _mark_reviewed(db_session, fx)
    await _settle(db_session, fx["team"])
    a, b = fx["student_ids"]
    ua, ub = fx["usernames"]
    before_b = await _total_points(db_session, b)

    r = await async_client.post(
        f"{BASE}/teams/{fx['team'].id}/peer-ratings",
        json=[{"rated_student_id": b, "score": 1}], headers=await _login_headers(async_client, ua),
    )
    assert r.status_code == 204, r.text
    assert await _total_points(db_session, b) == before_b  # still waiting for b's rating

    r = await async_client.post(
        f"{BASE}/teams/{fx['team'].id}/peer-ratings",
        json=[{"rated_student_id": a, "score": 5}], headers=await _login_headers(async_client, ub),
    )
    assert r.status_code == 204, r.text
    db_session.expire_all()
    assert await _total_points(db_session, b) - before_b == round(settings.TEAM_PROJECT_TEAM_BONUS * 0.5)


# ── scheduler sweep ─────────────────────────────────────────────────────────

async def test_sweep_pays_a_team_whose_review_landed_after_finalize(db_session, points_fixture):
    from app.scheduler import job_settle_team_projects
    fx = points_fixture
    await _mark_reviewed(db_session, fx)  # e.g. the stuck-review sweep graded it later
    team_id = fx["team"].id
    expected = _piece(fx, fx["lead_id"]) + settings.TEAM_PROJECT_LEAD_BONUS
    before = await _total_points(db_session, fx["lead_id"])

    await job_settle_team_projects()

    db_session.expire_all()
    team = (await db_session.execute(
        select(TeamProjectTeam).where(TeamProjectTeam.id == team_id)
    )).scalar_one()
    assert team.status == TeamStatus.reviewed
    assert await _total_points(db_session, fx["lead_id"]) - before == expected


# ── finalize ────────────────────────────────────────────────────────────────

async def _reopen_for_finalize(db_session, fx):
    fx["team"].status = TeamStatus.integrating
    fx["team"].final_project_id = None
    await db_session.commit()


async def test_finalize_refuses_a_private_repo_before_creating_anything(
    async_client, db_session, points_fixture,
):
    fx = points_fixture
    await _reopen_for_finalize(db_session, fx)
    headers = await _login_headers(async_client, fx["usernames"][0])
    with patch("app.api.v1.endpoints.team_project.github_repo_is_missing", new=AsyncMock(return_value=True)):
        r = await async_client.post(
            f"{BASE}/teams/{fx['team'].id}/finalize",
            json={"github_url": "https://github.com/acme/private"}, headers=headers,
        )
    assert r.status_code == 400, r.text
    await db_session.refresh(fx["team"])
    assert fx["team"].status == TeamStatus.integrating and fx["team"].final_project_id is None


async def test_finalize_with_a_successful_review_holds_back_only_the_team_bonus(
    async_client, db_session, points_fixture,
):
    fx = points_fixture
    await _reopen_for_finalize(db_session, fx)
    lead, member = fx["lead_id"], fx["student_ids"][1]
    piece_lead, piece_member = _piece(fx, lead), _piece(fx, member)
    before_lead = await _total_points(db_session, lead)
    before_member = await _total_points(db_session, member)

    async def fake_review(db, project, raise_on_error=False):
        project.grade, project.status, project.reviewed_at = "B", "Approved", utcnow()
        await db.commit()
        return {"success": True, "grade": "B", "new_points": 0}

    with patch("app.services.ai_review_service.run_ai_review_for_project", new=fake_review):
        r = await async_client.post(
            f"{BASE}/teams/{fx['team'].id}/finalize",
            json={"github_url": "https://github.com/acme/team"},
            headers=await _login_headers(async_client, fx["usernames"][0]),
        )
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "reviewed"
    db_session.expire_all()
    assert await _total_points(db_session, lead) - before_lead == piece_lead + settings.TEAM_PROJECT_LEAD_BONUS
    assert await _total_points(db_session, member) - before_member == piece_member


async def test_lead_can_finalize_again_after_a_rejection_without_review(
    async_client, db_session, points_fixture,
):
    fx = points_fixture
    fx["project"].status = "Rejected"
    fx["project"].github_url = "https://github.com/acme/old"
    fx["project"].instructor_feedback = "Repozitoriy bo'sh"
    await db_session.commit()
    project_id, team_id, lead_id = fx["project"].id, fx["team"].id, fx["lead_id"]
    headers = await _login_headers(async_client, fx["usernames"][0])
    unavailable = AsyncMock(return_value={"success": False, "http_status": 503, "reason": "AI o'chiq"})

    with patch("app.services.ai_review_service.run_ai_review_for_project", new=unavailable):
        r = await async_client.post(
            f"{BASE}/teams/{team_id}/finalize",
            json={"github_url": "https://github.com/acme/fixed"}, headers=headers,
        )
    assert r.status_code == 200, r.text

    db_session.expire_all()
    team = (await db_session.execute(
        select(TeamProjectTeam).where(TeamProjectTeam.id == team_id)
    )).scalar_one()
    assert team.final_project_id == project_id, "must reuse the same Project, not create another"
    project = (await db_session.execute(select(Project).where(Project.id == project_id))).scalar_one()
    assert project.github_url == "https://github.com/acme/fixed"
    assert project.status == "Submitted"
    lead_projects = (await db_session.execute(
        select(Project).where(Project.student_id == lead_id)
    )).scalars().all()
    assert len(lead_projects) == 1

    # Still submitted & unreviewed now (AI down) -> a third call is the normal 409.
    with patch("app.services.ai_review_service.run_ai_review_for_project", new=unavailable):
        r = await async_client.post(
            f"{BASE}/teams/{team_id}/finalize",
            json={"github_url": "https://github.com/acme/fixed"}, headers=headers,
        )
    assert r.status_code == 409


async def test_my_endpoint_tells_the_lead_to_finalize_again(async_client, db_session, points_fixture):
    fx = points_fixture
    fx["project"].status = "Rejected"
    fx["project"].instructor_feedback = "Repozitoriy bo'sh"
    await db_session.commit()

    r = await async_client.get(f"{BASE}/my", headers=await _login_headers(async_client, fx["usernames"][0]))
    assert r.status_code == 200, r.text
    team = r.json()[0]["my_team"]
    assert team["can_refinalize"] is True
    assert team["final_feedback"] == "Repozitoriy bo'sh"

    # A reviewed rejection (a real low grade) is final: no second finalize.
    fx["project"].reviewed_at = utcnow()
    await db_session.commit()
    r = await async_client.get(f"{BASE}/my", headers=await _login_headers(async_client, fx["usernames"][0]))
    assert r.json()[0]["my_team"]["can_refinalize"] is False
