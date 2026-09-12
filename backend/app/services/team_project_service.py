"""Team formation for the team-projects feature — random teams, each with
its own independently-random theme + tech stack (see
app/services/team_project_constants.py for the pools and
app/services/team_project_planner.py for what happens next, per-team).
"""
import json
import random
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.team_game_common import spawn_background_task
from app.models.group import Group
from app.models.team_project import (
    TeamProject, TeamProjectTeam, TeamProjectMember, TeamProjectEvent, TeamRole,
)
from app.schemas.team_project import SkillProfile
from app.services import skill_profile_service
from app.services.team_project_constants import THEMES, TECH_STACKS

# Order used to rank current_level for auto-picking the strongest member as
# lead — matches the level progression in app/models/user.py::StudentLevel.
_LEVEL_RANK = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}


def _cycle_sample(pool: list, count: int) -> list:
    """count independent draws from pool, reshuffling each time the pool is
    exhausted — keeps consecutive teams from getting the same value back to
    back (when count <= len(pool)) while never blocking on a fixed pool
    size, and stays truly random rather than a plain round-robin."""
    picks: list = []
    remaining: list = []
    while len(picks) < count:
        if not remaining:
            remaining = pool[:]
            random.shuffle(remaining)
        picks.append(remaining.pop())
    return picks


async def create_team_project(
        db: AsyncSession, *, group_id: int, course_id: Optional[int],
        teacher_id: int, team_size: int, deadline_days: int,
) -> TeamProject:
    group = (await db.execute(
        select(Group).where(Group.id == group_id)
    )).scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")

    students = list(group.students)
    if len(students) < 2:
        raise HTTPException(
            status_code=400,
            detail="Jamoa tuzish uchun guruhda kamida 2 ta o'quvchi bo'lishi kerak",
        )

    profiles_by_id = {
        p.student_id: p
        for p in await skill_profile_service.build_group_skill_profiles(db, group_id)
    }

    team_project = TeamProject(
        group_id=group_id, course_id=course_id, teacher_id=teacher_id,
        team_size=team_size, deadline_days=deadline_days,
    )
    db.add(team_project)
    await db.flush()

    shuffled = students[:]
    random.shuffle(shuffled)
    chunks: List[list] = []
    for i in range(0, len(shuffled), team_size):
        chunk = shuffled[i:i + team_size]
        # Fold a too-small trailing chunk into the previous team rather than
        # leaving a lone-member "team".
        if len(chunk) < 2 and chunks:
            chunks[-1].extend(chunk)
        else:
            chunks.append(chunk)

    themes = _cycle_sample(THEMES, len(chunks))
    stacks = _cycle_sample(TECH_STACKS, len(chunks))

    teams: List[TeamProjectTeam] = []
    for idx, members in enumerate(chunks):
        team = TeamProjectTeam(
            team_project_id=team_project.id,
            name=f"Team {idx + 1}",
            theme=themes[idx]["key"],
            tech_stack=stacks[idx]["key"],
        )
        db.add(team)
        await db.flush()

        lead_student_id = _pick_lead(members, profiles_by_id)
        for student in members:
            profile = profiles_by_id.get(student.id)
            db.add(TeamProjectMember(
                team_id=team.id,
                student_id=student.id,
                role=TeamRole.lead if student.id == lead_student_id else TeamRole.member,
                level_at_assignment=(profile.current_level.value if profile else student.current_level.value),
                skill_summary_at_assignment=(profile.summary if profile else ""),
            ))
        team.lead_student_id = lead_student_id
        db.add(TeamProjectEvent(
            team_project_id=team_project.id, team_id=team.id,
            event_type="team_formed",
            payload_json=json.dumps({
                "member_ids": [s.id for s in members],
                "lead_student_id": lead_student_id,
                "theme": team.theme, "tech_stack": team.tech_stack,
            }),
        ))
        teams.append(team)

    await db.commit()
    await db.refresh(team_project)

    from app.services.team_project_planner import generate_plan_for_team_standalone
    for team in teams:
        spawn_background_task(generate_plan_for_team_standalone(team.id))

    return team_project


def _pick_lead(members: list, profiles_by_id: dict[int, SkillProfile]) -> int:
    def rank(student):
        profile = profiles_by_id.get(student.id)
        level = profile.current_level.value if profile else student.current_level.value
        points = profile.lifetime_points if profile else (student.lifetime_points or 0)
        return (_LEVEL_RANK.get(level, 0), points)

    return max(members, key=rank).id
