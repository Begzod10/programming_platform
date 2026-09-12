"""Points awarding for a finalized Team Project team — per-piece points by
required level, a team bonus gated on the final grade, a lead bonus, and a
peer-rating modifier that halves a low-rated member's team bonus.

Hook point (documented per the spec's own request to flag this choice):
called directly from team_project.py::finalize_team, right after
project_service.submit_project(...) returns — submit_project runs the AI
review SYNCHRONOUSLY (see ai_review_service.run_ai_review_for_project),
so project.reviewed_at/grade are already set by the time finalize_team's
handler continues. This is the least invasive option: it doesn't touch
ai_review_service.py or project_service.py at all, both of which are
shared across every project on the platform, not just team ones.

IMPORTANT, found while building this — NOT obvious from the spec: do not
call both wallet_service.record_earn AND RankingService.add_points_to_student
for the same amount. record_earn's _write_ledger mutates
student.total_points itself; add_points_to_student ALSO mutates
total_points (plus lifetime_points + Ranking). Calling both with the same
amount double-counts total_points. Fixed here by inserting the
WalletLedgerEntry row FIRST inside a SAVEPOINT (the unique idempotency_key
constraint is the actual atomic "claim" — only one concurrent caller can
win the insert), and only calling add_points_to_student after that insert
succeeds. A duplicate key's insert fails, the savepoint rolls back
in isolation (not the outer transaction — so a batch of several awards in
one call isn't wiped by one duplicate), and add_points_to_student is never
invoked for that duplicate. NOT independently verified against real
concurrent Postgres connections — same caveat as the earlier Points TOCTOU
fix in ranking_service.py.
"""
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.project import Project
from app.models.store import LedgerReason, WalletLedgerEntry
from app.models.team_project import (
    TeamProjectPeerRating, TeamProjectTask, TeamProjectTeam, TaskStatus,
)
from app.models.user import Student
from app.services.ranking_service import RankingService

logger = logging.getLogger(__name__)

# Lower = better — same order grok_review.py's _VALID_GRADES_ORDER uses.
_GRADE_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3, "F": 4}
_MIN_PIECE_POINTS = 10
_PEER_RATING_THRESHOLD = 2.5
_MIN_PEER_RATINGS_FOR_MODIFIER = 2


async def _award_once(
    db: AsyncSession, *, student_id: int, amount: int,
    ref_type: str, ref_id: Optional[int], idempotency_key: str, note: str,
) -> bool:
    """Claims `idempotency_key` via a SAVEPOINT-isolated ledger insert,
    then applies the points exactly once if the claim succeeded. Returns
    True if this call actually applied new points, False if it was a
    no-op (already awarded by an earlier call with the same key)."""
    if amount <= 0:
        return False

    entry = WalletLedgerEntry(
        student_id=student_id, delta_coins=amount, reason=LedgerReason.earn_team_project,
        ref_type=ref_type, ref_id=ref_id, idempotency_key=idempotency_key,
        balance_after=0,  # corrected below once we know this claim won
        note=note,
    )
    try:
        async with db.begin_nested():
            db.add(entry)
            await db.flush()
    except IntegrityError:
        logger.info("[team-points] idempotency_key=%s already claimed, skipping", idempotency_key)
        return False

    await RankingService(db).add_points_to_student(student_id, amount)
    student = (await db.execute(select(Student).where(Student.id == student_id))).scalar_one()
    entry.balance_after = student.total_points
    await db.flush()
    return True


def _piece_points(required_level: str, ai_score: Optional[int]) -> int:
    base = settings.TEAM_PROJECT_PIECE_POINTS.get(required_level, settings.TEAM_PROJECT_PIECE_POINTS["Beginner"])
    score = ai_score if ai_score is not None else 0
    return max(_MIN_PIECE_POINTS, round(base * score / 100))


async def _peer_modifier(db: AsyncSession, team_id: int, student_id: int) -> float:
    """1.0 normally; 0.5 if this member's average peer rating is below the
    threshold with enough ratings to be meaningful; never goes below 0
    (the multiplier itself is never negative — "never below 0" in the spec
    means the resulting bonus amount, which max(0, ...) downstream via the
    multiplier floor of 0.5 here already guarantees for a positive base)."""
    rows = (await db.execute(
        select(TeamProjectPeerRating.score).where(
            TeamProjectPeerRating.team_id == team_id,
            TeamProjectPeerRating.rated_student_id == student_id,
        )
    )).scalars().all()
    if len(rows) < _MIN_PEER_RATINGS_FOR_MODIFIER:
        return 1.0
    avg = sum(rows) / len(rows)
    return 0.5 if avg < _PEER_RATING_THRESHOLD else 1.0


async def award_points(db: AsyncSession, team: TeamProjectTeam) -> dict:
    """Awards per-piece points, the team bonus (if earned), and the lead
    bonus — all idempotent, safe to call more than once for the same team
    (only the first call for each (student, award-kind) pair actually
    pays out). Returns a summary dict for the caller to log/inspect."""
    tasks = (await db.execute(
        select(TeamProjectTask).where(TeamProjectTask.team_id == team.id)
    )).scalars().all()

    awarded: dict[str, int] = {}
    for task in tasks:
        if task.status != TaskStatus.approved or task.assigned_student_id is None:
            continue
        points = _piece_points(task.required_level, task.ai_score)
        applied = await _award_once(
            db, student_id=task.assigned_student_id, amount=points,
            ref_type="team_project_task", ref_id=task.id,
            idempotency_key=f"teamproj:{team.team_project_id}:task:{task.id}:{task.assigned_student_id}",
            note=f"Team project piece: {task.title}",
        )
        if applied:
            task.points_awarded = points
            awarded[f"task:{task.id}"] = points

    final_project = None
    if team.final_project_id:
        final_project = (await db.execute(
            select(Project).where(Project.id == team.final_project_id)
        )).scalar_one_or_none()

    team_bonus_earned = bool(
        final_project and final_project.grade
        and _GRADE_ORDER.get(final_project.grade, 99) <= _GRADE_ORDER["B"]
    )

    if team_bonus_earned:
        from app.models.team_project import TeamProjectMember
        members = (await db.execute(
            select(TeamProjectMember).where(TeamProjectMember.team_id == team.id)
        )).scalars().all()
        for member in members:
            modifier = await _peer_modifier(db, team.id, member.student_id)
            bonus = round(settings.TEAM_PROJECT_TEAM_BONUS * modifier)
            applied = await _award_once(
                db, student_id=member.student_id, amount=bonus,
                ref_type="team_project_team", ref_id=team.id,
                idempotency_key=f"teamproj:{team.team_project_id}:team:{team.id}:team_bonus:{member.student_id}",
                note="Team project team bonus" + (" (peer rating modifier applied)" if modifier < 1 else ""),
            )
            if applied:
                awarded[f"team_bonus:{member.student_id}"] = bonus

        if team.lead_student_id:
            applied = await _award_once(
                db, student_id=team.lead_student_id, amount=settings.TEAM_PROJECT_LEAD_BONUS,
                ref_type="team_project_team", ref_id=team.id,
                # Scoped by team_id, not just team_project_id — a project
                # with multiple teams has multiple leads, each needing
                # their own key. The spec's literal
                # "...:lead_bonus" (no team_id) would collide across
                # teams in the same project; fixed here, flagging the
                # deviation.
                idempotency_key=f"teamproj:{team.team_project_id}:team:{team.id}:lead_bonus",
                note="Team project lead/integrator bonus",
            )
            if applied:
                awarded["lead_bonus"] = settings.TEAM_PROJECT_LEAD_BONUS

    await db.commit()
    return {"team_bonus_earned": team_bonus_earned, "awarded": awarded}
