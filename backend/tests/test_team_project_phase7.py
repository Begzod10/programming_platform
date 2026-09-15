"""Tests for Phase 7 wiring: team-project achievements, public-profile
team-project section, and the parent-bot notify helper.

Built directly against models (a reviewed team + final Project), same
approach test_team_project_points.py uses — no need to run the full AI
pipeline for these checks.
"""
import uuid

import pytest_asyncio
from sqlalchemy import select

from app.models.group import Group, student_groups
from app.models.project import Project
from app.models.team_project import (
    TeamProject, TeamProjectTeam, TeamProjectMember, TeamRole, TeamStatus,
)
from app.models.user import Student
from app.services.achievement_service import check_and_award_achievements
from app.models.student_achievement import StudentAchievement
from app.models.achievement import Achievement

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


@pytest_asyncio.fixture
async def reviewed_team(async_client, db_session):
    """A reviewed team of 2 (student_ids[0] is lead), final project graded B."""
    uid = uuid.uuid4().hex[:8]
    student_ids, usernames = [], []
    for i in range(2):
        sid, uname = await _register(async_client, f"p7_{uid}_{i}")
        student_ids.append(sid)
        usernames.append(uname)

    teacher_id, _ = await _register(async_client, f"p7t_{uid}")
    teacher = (await db_session.execute(select(Student).where(Student.id == teacher_id))).scalar_one()
    teacher.role = "teacher"
    group = Group(name="Phase7 Group", teacher_id=teacher_id)
    db_session.add(group)
    await db_session.flush()
    for sid in student_ids:
        await db_session.execute(student_groups.insert().values(student_id=sid, group_id=group.id))

    tp = TeamProject(group_id=group.id, teacher_id=teacher_id, status="active")
    db_session.add(tp)
    await db_session.flush()

    final_project = Project(
        student_id=student_ids[0], title="Mini CRM", description="d",
        difficulty_level="Easy", status="Approved", points_earned=90, grade="B",
    )
    db_session.add(final_project)
    await db_session.flush()

    team = TeamProjectTeam(
        team_project_id=tp.id, name="Team 1", lead_student_id=student_ids[0],
        status=TeamStatus.reviewed, project_title="Mini CRM",
        final_project_id=final_project.id,
    )
    db_session.add(team)
    await db_session.flush()
    for i, sid in enumerate(student_ids):
        db_session.add(TeamProjectMember(
            team_id=team.id, student_id=sid,
            role=TeamRole.lead if i == 0 else TeamRole.member,
            level_at_assignment="Beginner", skill_summary_at_assignment="x",
        ))
    await db_session.commit()

    return {"team": team, "student_ids": student_ids, "usernames": usernames}


async def test_lead_gets_all_three_team_achievements(db_session, reviewed_team):
    fx = reviewed_team
    lead_id = fx["student_ids"][0]
    await check_and_award_achievements(db_session, lead_id)

    earned = (await db_session.execute(
        select(Achievement.criteria_type)
        .join(StudentAchievement, StudentAchievement.achievement_id == Achievement.id)
        .where(StudentAchievement.student_id == lead_id)
    )).scalars().all()
    assert "team_project_count" in earned
    assert "team_lead_count" in earned
    assert "team_bonus_count" in earned  # grade B qualifies


async def test_member_gets_participation_and_bonus_but_not_lead(db_session, reviewed_team):
    fx = reviewed_team
    member_id = fx["student_ids"][1]
    await check_and_award_achievements(db_session, member_id)

    earned = (await db_session.execute(
        select(Achievement.criteria_type)
        .join(StudentAchievement, StudentAchievement.achievement_id == Achievement.id)
        .where(StudentAchievement.student_id == member_id)
    )).scalars().all()
    assert "team_project_count" in earned
    assert "team_bonus_count" in earned
    assert "team_lead_count" not in earned


async def test_no_team_bonus_achievement_when_grade_below_b(db_session, reviewed_team):
    fx = reviewed_team
    # Downgrade the final project's grade below the bonus threshold.
    final_project = (await db_session.execute(
        select(Project).where(Project.id == fx["team"].final_project_id)
    )).scalar_one()
    final_project.grade = "D"
    await db_session.commit()

    member_id = fx["student_ids"][1]
    await check_and_award_achievements(db_session, member_id)

    earned = (await db_session.execute(
        select(Achievement.criteria_type)
        .join(StudentAchievement, StudentAchievement.achievement_id == Achievement.id)
        .where(StudentAchievement.student_id == member_id)
    )).scalars().all()
    assert "team_project_count" in earned
    assert "team_bonus_count" not in earned


async def test_check_is_idempotent_no_duplicate_rows(db_session, reviewed_team):
    fx = reviewed_team
    lead_id = fx["student_ids"][0]
    await check_and_award_achievements(db_session, lead_id)
    await check_and_award_achievements(db_session, lead_id)  # second call, same team

    count = (await db_session.execute(
        select(StudentAchievement)
        .join(Achievement, Achievement.id == StudentAchievement.achievement_id)
        .where(
            StudentAchievement.student_id == lead_id,
            Achievement.criteria_type == "team_project_count",
        )
    )).scalars().all()
    assert len(count) == 1


async def test_public_profile_lists_team_project_with_role_and_bonus(async_client, db_session, reviewed_team):
    fx = reviewed_team
    lead_username = fx["usernames"][0]

    resp = await async_client.get(f"/api/v1/student/public/{lead_username}")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body["team_projects"]) == 1
    tp = body["team_projects"][0]
    assert tp["project_title"] == "Mini CRM"
    assert tp["was_lead"] is True
    assert tp["team_bonus_earned"] is True


async def test_public_profile_member_not_marked_as_lead(async_client, db_session, reviewed_team):
    fx = reviewed_team
    member_username = fx["usernames"][1]

    resp = await async_client.get(f"/api/v1/student/public/{member_username}")
    assert resp.status_code == 200, resp.text
    tp = resp.json()["team_projects"][0]
    assert tp["was_lead"] is False
    assert tp["team_bonus_earned"] is True


async def test_public_profile_excludes_unreviewed_teams(async_client, db_session, reviewed_team):
    fx = reviewed_team
    fx["team"].status = TeamStatus.working
    await db_session.commit()

    resp = await async_client.get(f"/api/v1/student/public/{fx['usernames'][0]}")
    assert resp.status_code == 200, resp.text
    assert resp.json()["team_projects"] == []
