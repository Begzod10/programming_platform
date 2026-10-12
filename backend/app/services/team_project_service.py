"""Team formation for the team-projects feature — skill-balanced teams
(see _form_balanced_teams), each with its own independently-random theme +
tech stack (see app/services/team_project_constants.py for the pools and
app/services/team_project_planner.py for what happens next, per-team).
"""
import json
import random
import re
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.team_game_common import spawn_background_task
from app.models.group import Group
from app.models.team_project import (
    TeamProject, TeamProjectTeam, TeamProjectMember, TeamProjectEvent, TeamRole,
    TeamProjectStatus,
)
from app.models.user import Student
from app.schemas.team_project import SkillProfile
from app.services import skill_profile_service
from app.services.team_project_skills import build_skill_levels
from app.services.team_project_constants import THEMES, TECH_STACKS, LEVEL_RANK as _LEVEL_RANK
from app.services.teacher_students import teacher_student_ids_subquery

# _LEVEL_RANK ranks current_level for auto-picking the strongest member as
# lead — matches the level progression in app/models/user.py::StudentLevel.
# Shared with team_project_planner.py's plan validation; see
# team_project_constants.py.

# A group only frees up for a new assignment once its current one is fully
# wrapped up — reviewed (graded) or cancelled by a teacher. Anything else
# (planning/pending_approval/active/integrating/submitted) still counts as
# "this group already has a team project" — teams are mid-work, submitted-
# but-not-yet-graded, etc.
_OPEN_STATUSES = [
    s for s in TeamProjectStatus
    if s not in (TeamProjectStatus.reviewed, TeamProjectStatus.cancelled)
]


def _cycle_sample(pool: list, count: int, avoid_key: Optional[str] = None) -> list:
    """count independent draws from pool, reshuffling each time the pool is
    exhausted — keeps consecutive teams from getting the same value back to
    back (when count <= len(pool)) while never blocking on a fixed pool
    size, and stays truly random rather than a plain round-robin.

    avoid_key: excluded from the very first reshuffle only (e.g. the theme
    the previous assignment happened to land on) — with a 6-entry pool, two
    separate one-team assignments in a row have a 1-in-6 chance of drawing
    the same theme purely by chance, which reads as "always the same" to a
    teacher testing back to back. Only the first draw is constrained; later
    reshuffles (once count exceeds the pool size) use the full pool again.
    """
    first_pool = [p for p in pool if p["key"] != avoid_key] if avoid_key else pool
    picks: list = []
    remaining: list = []
    while len(picks) < count:
        if not remaining:
            remaining = (first_pool if not picks else pool)[:]
            random.shuffle(remaining)
        picks.append(remaining.pop())
    return picks


async def past_themes_by_student(db: AsyncSession, student_ids: List[int]) -> dict[int, set]:
    """{student_id: themes of every team they were ever on} — so a new team can avoid a theme its
    members already built (a random draw gave about 1 in 7 students the same theme again)."""
    if not student_ids:
        return {}
    rows = (await db.execute(
        select(TeamProjectMember.student_id, TeamProjectTeam.theme)
        .join(TeamProjectTeam, TeamProjectTeam.id == TeamProjectMember.team_id)
        .where(TeamProjectMember.student_id.in_(student_ids), TeamProjectTeam.theme.isnot(None))
    )).all()
    out: dict[int, set] = {}
    for sid, theme in rows:
        out.setdefault(sid, set()).add(theme)
    return out


def choose_themes_for_teams(
        member_ids: List[List[int]], past_themes: dict, rng=random, avoid_key: Optional[str] = None,
) -> List[dict]:
    """One theme per team: the one the fewest of its members already built, preferring a theme no
    other team of this assignment took (while the pool lasts). Ties are random; `avoid_key` (the
    teacher's previous team) only breaks ties — history matters more than "not the last one"."""
    picks: List[dict] = []
    taken: set = set()
    for members in member_ids:
        def score(theme: dict):
            repeats = sum(1 for m in members if theme["key"] in past_themes.get(m, ()))
            return (theme["key"] in taken, repeats)

        best = min(score(t) for t in THEMES)
        tied = [t for t in THEMES if score(t) == best]
        calmer = [t for t in tied if t["key"] != avoid_key]
        choice = rng.choice(calmer or tied)
        picks.append(choice)
        taken.add(choice["key"])
        if len(taken) >= len(THEMES):
            taken.clear()             # more teams than themes: start another round
    return picks


class NoFittingStack(Exception):
    """No tech stack — not even plain JavaScript — fits a team's skills."""


def stack_fits(stack: dict, skills: List[dict]) -> bool:
    """Can this team do this stack? `skills[i]` is member i's {area: AreaSkill}.
    At least half the team must have the stack's frontend area AND at least one member
    its backend area (any of `requires.backend`). An area nobody can have (no course
    exists for it, e.g. Vue) never fits — a stack must never be handed out on a guess."""
    req = stack.get("requires")
    if not req or not skills:
        return False
    frontend = req["frontend"]
    have_frontend = sum(1 for m in skills if m.get(frontend) is not None and m[frontend].has)
    have_backend = any(m.get(a) is not None and m[a].has for m in skills for a in req["backend"])
    return have_frontend > 0 and have_frontend * 2 >= len(skills) and have_backend


def pick_stacks_for_teams(
        member_skills: List[List[dict]], drawn: List[dict], rng=random,
) -> List[dict]:
    """One stack per team. Keep the random draw (`drawn`) when it fits the team; otherwise
    take a random fitting stack, avoiding the previous team's stack when another one fits.
    Raises NoFittingStack when nothing fits (nobody can do even plain JavaScript + a backend)."""
    picks: List[dict] = []
    for i, skills in enumerate(member_skills):
        choice = drawn[i]
        if not stack_fits(choice, skills):
            fitting = [s for s in TECH_STACKS if stack_fits(s, skills)]
            if not fitting:
                raise NoFittingStack()
            varied = [s for s in fitting if not picks or s["key"] != picks[-1]["key"]]
            choice = rng.choice(varied or fitting)
        picks.append(choice)
    return picks


async def create_team_project(
        db: AsyncSession, *, group_id: int, course_id: Optional[int],
        teacher_id: int, team_size: int, deadline_days: int, student_ids: List[int],
) -> TeamProject:
    group = (await db.execute(
        select(Group).where(Group.id == group_id)
    )).scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")

    # student_ids is the teacher's explicit pick — NOT necessarily
    # group.students. It can include students from the teacher's other
    # groups/flows (see teacher_student_ids_subquery) and can leave out
    # students in `group` who won't be participating this round. Every id
    # still has to belong to a group/flow this teacher actually owns —
    # otherwise a teacher could staff another teacher's student onto a
    # team without them ever being reachable/notified through their own
    # roster.
    requested_ids = set(student_ids)
    reachable = teacher_student_ids_subquery(teacher_id)
    allowed_ids = set((await db.execute(
        select(reachable.c.student_id).where(reachable.c.student_id.in_(requested_ids))
    )).scalars().all())
    invalid_ids = requested_ids - allowed_ids
    if invalid_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Studentlar sizning guruhlaringizga tegishli emas: {sorted(invalid_ids)}",
        )

    students = (await db.execute(
        select(Student).where(Student.id.in_(requested_ids))
    )).scalars().all()
    if len(students) < 2:
        raise HTTPException(
            status_code=400,
            detail="Jamoa tuzish uchun kamida 2 ta o'quvchi tanlanishi kerak",
        )

    existing = (await db.execute(
        select(TeamProject.id)
        .where(TeamProject.group_id == group_id, TeamProject.status.in_(_OPEN_STATUSES))
        .limit(1)
    )).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="Bu guruh uchun allaqachon faol jamoaviy loyiha bor — "
                    "yangisini yaratishdan oldin avvalgisi yakunlanishi yoki bekor qilinishi kerak",
        )

    profiles_by_id = {
        p.student_id: p
        for p in await skill_profile_service.build_profiles_for_student_ids(db, list(requested_ids))
    }

    chunks = _form_balanced_teams(students, team_size, profiles_by_id)

    # Decide every team's stack BEFORE anything is written: when no stack fits a team, the
    # request fails cleanly instead of leaving a half-created project behind.
    skills_by_id = await build_skill_levels(db, [s.id for s in students])
    last_theme, last_stack = await _last_used_theme_and_stack(db, teacher_id)
    themes = choose_themes_for_teams(
        [[s.id for s in members] for members in chunks],
        await past_themes_by_student(db, [s.id for s in students]),
        avoid_key=last_theme,
    )
    try:
        stacks = pick_stacks_for_teams(
            [[skills_by_id[s.id] for s in members] for members in chunks],
            _cycle_sample(TECH_STACKS, len(chunks), avoid_key=last_stack),
        )
    except NoFittingStack:
        raise HTTPException(
            status_code=400,
            detail="Tanlangan o'quvchilar uchun mos texnologiya topilmadi: JavaScript va backend "
                   "(Flask/Python) kurslari yetarli tugatilmagan",
        )

    team_project = TeamProject(
        group_id=group_id, course_id=course_id, teacher_id=teacher_id,
        team_size=team_size, deadline_days=deadline_days,
    )
    db.add(team_project)
    await db.flush()

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


async def _last_used_theme_and_stack(db: AsyncSession, teacher_id: int):
    """Most recent team this teacher formed, if any — used to bias the next
    assignment's first draw away from an immediate repeat (see _cycle_sample)."""
    row = (await db.execute(
        select(TeamProjectTeam.theme, TeamProjectTeam.tech_stack)
        .join(TeamProject, TeamProject.id == TeamProjectTeam.team_project_id)
        .where(TeamProject.teacher_id == teacher_id)
        .order_by(desc(TeamProjectTeam.created_at))
        .limit(1)
    )).first()
    return (row[0], row[1]) if row else (None, None)


def _skill_rank(student, profiles_by_id: dict[int, SkillProfile]) -> tuple[int, int]:
    profile = profiles_by_id.get(student.id)
    level = profile.current_level.value if profile else student.current_level.value
    points = profile.lifetime_points if profile else (student.lifetime_points or 0)
    return (_LEVEL_RANK.get(level, 0), points)


def _pick_lead(members: list, profiles_by_id: dict[int, SkillProfile]) -> int:
    return max(members, key=lambda s: _skill_rank(s, profiles_by_id)).id


def _team_count(total_students: int, team_size: int) -> int:
    """Same team-count semantics the old contiguous-chunking code produced
    (a lone trailing member folds into the previous team instead of
    standing alone), factored out so _form_balanced_teams can pre-size its
    buckets before distributing anyone into them."""
    full_teams, remainder = divmod(total_students, team_size)
    if remainder == 0:
        return max(full_teams, 1)
    if remainder == 1 and full_teams >= 1:
        return full_teams
    return full_teams + 1


def _form_balanced_teams(
        students: list, team_size: int, profiles_by_id: dict[int, SkillProfile],
) -> List[list]:
    """Skill-balanced team formation via a snake draft, replacing a plain
    random shuffle: sort students strongest-to-weakest by _skill_rank, then
    hand them out to `_team_count(...)` teams in serpentine order (0, 1,
    ..., K-1, K-1, ..., 1, 0, 0, 1, ...) the way a sports league drafts
    players — round 1 gives each team one strong pick, round 2 reverses
    direction so no team is stuck always picking last, and so on. This
    keeps each team's overall skill mix close to even instead of letting a
    random shuffle occasionally cluster every strong (or every struggling)
    student from a group onto one team.
    """
    ordered = sorted(students, key=lambda s: _skill_rank(s, profiles_by_id), reverse=True)
    num_teams = _team_count(len(students), team_size)
    teams: List[list] = [[] for _ in range(num_teams)]

    idx, direction = 0, 1
    for student in ordered:
        teams[idx].append(student)
        next_idx = idx + direction
        if next_idx < 0 or next_idx >= num_teams:
            direction *= -1
        else:
            idx = next_idx

    return teams
