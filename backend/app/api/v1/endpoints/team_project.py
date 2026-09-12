import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_db, get_current_teacher, get_current_student
from app.models.group import Group
from app.models.user import Student
from app.models.team_project import (
    TeamProject, TeamProjectTeam, TeamProjectMember, TeamProjectTask,
    TeamProjectEvent, TeamProjectPeerRating, TaskStatus, TeamStatus, TeamProjectStatus,
)
from app.schemas.team_project import (
    TeamProjectCreate, TeamProjectRead, TeamRead, TaskRead, MemberRead,
    MyTeamProjectRead, TaskSubmitBody, ReassignBody, FinalizeBody, PeerRatingItem,
)
from app.services.team_project_service import create_team_project
from app.services.team_project_planner import generate_plan_for_team, MAX_GENERATION_ATTEMPTS
from app.services.team_project_task_review import review_task_submission
from app.services.team_project_constants import THEMES_BY_KEY, TECH_STACKS_BY_KEY
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate
from app.utils.datetime_utils import utcnow

router = APIRouter(redirect_slashes=False)


def _team_load_options():
    return [
        selectinload(TeamProject.teams).selectinload(TeamProjectTeam.members).selectinload(
            TeamProjectMember.student
        ),
        selectinload(TeamProject.teams).selectinload(TeamProjectTeam.tasks).selectinload(
            TeamProjectTask.assigned_student
        ),
    ]


async def _fetch_team_project(db: AsyncSession, team_project_id: int) -> TeamProject:
    tp = (await db.execute(
        select(TeamProject)
        .where(TeamProject.id == team_project_id)
        .options(*_team_load_options())
    )).unique().scalar_one_or_none()
    if tp is None:
        raise HTTPException(status_code=404, detail="Team-project topilmadi")
    return tp


def _task_read(task: TeamProjectTask) -> TaskRead:
    return TaskRead(
        id=task.id, order=task.order, title=task.title, title_ru=task.title_ru,
        description=task.description, description_ru=task.description_ru,
        required_level=task.required_level,
        interface_contract=json.loads(task.interface_contract_json or "{}"),
        acceptance_criteria=json.loads(task.acceptance_criteria_json or "[]"),
        depends_on=json.loads(task.depends_on_json or "[]"),
        estimated_hours=task.estimated_hours, status=task.status.value,
        assigned_student_id=task.assigned_student_id,
        assigned_student_name=(
            (task.assigned_student.full_name or task.assigned_student.username)
            if task.assigned_student else None
        ),
        submission_url=task.submission_url,
        ai_score=task.ai_score,
        ai_feedback=json.loads(task.ai_feedback_json) if task.ai_feedback_json else None,
        deadline_at=task.deadline_at,
    )


def _team_read(team: TeamProjectTeam) -> TeamRead:
    theme = THEMES_BY_KEY.get(team.theme)
    stack = TECH_STACKS_BY_KEY.get(team.tech_stack)
    return TeamRead(
        id=team.id, name=team.name, status=team.status.value,
        theme=team.theme, theme_label=theme["label"] if theme else team.theme,
        tech_stack=team.tech_stack, tech_stack_label=stack["label"] if stack else team.tech_stack,
        project_title=team.project_title, project_description=team.project_description,
        lead_student_id=team.lead_student_id, final_project_id=team.final_project_id,
        generation_attempts=team.generation_attempts,
        members=[
            MemberRead(
                student_id=m.student_id,
                full_name=(m.student.full_name or m.student.username) if m.student else str(m.student_id),
                role=m.role.value, level_at_assignment=m.level_at_assignment,
            )
            for m in team.members
        ],
        tasks=[_task_read(t) for t in team.tasks],
    )


def _redact_team_read_for_other_student(team: TeamProjectTeam) -> TeamRead:
    """Same as _team_read but for a team the viewer is NOT a member of —
    drops skill levels and task detail (score, feedback, submission URL).
    Per the spec's own guardrail: "Students never see other members' skill
    summaries, points, or level snapshots" — /my used to call _team_read
    unconditionally for every team in the project, leaking exactly this
    (plus every other team's task submissions/AI scores) to any student in
    the same team_project. Found while reviewing this endpoint, not
    reported; fixed here rather than just flagged given the severity."""
    theme = THEMES_BY_KEY.get(team.theme)
    stack = TECH_STACKS_BY_KEY.get(team.tech_stack)
    return TeamRead(
        id=team.id, name=team.name, status=team.status.value,
        theme=team.theme, theme_label=theme["label"] if theme else team.theme,
        tech_stack=team.tech_stack, tech_stack_label=stack["label"] if stack else team.tech_stack,
        project_title=team.project_title, project_description=team.project_description,
        lead_student_id=team.lead_student_id, final_project_id=team.final_project_id,
        generation_attempts=team.generation_attempts,
        members=[
            MemberRead(
                student_id=m.student_id,
                full_name=(m.student.full_name or m.student.username) if m.student else str(m.student_id),
                role=m.role.value, level_at_assignment="",
            )
            for m in team.members
        ],
        tasks=[],
    )


def _team_project_read(tp: TeamProject) -> TeamProjectRead:
    """Full, unredacted detail — teacher-only (create_assignment,
    list_assignments, get_assignment all require get_current_teacher)."""
    return TeamProjectRead(
        id=tp.id, group_id=tp.group_id, course_id=tp.course_id, status=tp.status.value,
        team_size=tp.team_size, deadline_days=tp.deadline_days, created_at=tp.created_at,
        teams=[_team_read(t) for t in tp.teams],
    )


def _team_project_read_for_student(tp: TeamProject, my_team_id: int) -> TeamProjectRead:
    """Same shape as _team_project_read, but every team other than the
    caller's own is redacted — see _redact_team_read_for_other_student."""
    return TeamProjectRead(
        id=tp.id, group_id=tp.group_id, course_id=tp.course_id, status=tp.status.value,
        team_size=tp.team_size, deadline_days=tp.deadline_days, created_at=tp.created_at,
        teams=[
            _team_read(t) if t.id == my_team_id else _redact_team_read_for_other_student(t)
            for t in tp.teams
        ],
    )


def _find_team_and_membership(tp: TeamProject, student_id: int):
    for team in tp.teams:
        for m in team.members:
            if m.student_id == student_id:
                return team, m
    return None, None


# ── Teacher: create assignment ──────────────────────────────────────────────
@router.post("", response_model=TeamProjectRead, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=TeamProjectRead, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_assignment(
        body: TeamProjectCreate,
        db: AsyncSession = Depends(get_db),
        teacher: Student = Depends(get_current_teacher),
):
    group = (await db.execute(select(Group).where(Group.id == body.group_id))).scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")
    if group.teacher_id is not None and group.teacher_id != teacher.id:
        raise HTTPException(status_code=403, detail="Bu guruh sizga tegishli emas")

    tp = await create_team_project(
        db, group_id=body.group_id, course_id=body.course_id, teacher_id=teacher.id,
        team_size=body.team_size, deadline_days=body.deadline_days,
    )
    tp = await _fetch_team_project(db, tp.id)
    return _team_project_read(tp)


# ── Teacher: list ────────────────────────────────────────────────────────────
@router.get("", response_model=list[TeamProjectRead])
@router.get("/", response_model=list[TeamProjectRead], include_in_schema=False)
async def list_assignments(
        db: AsyncSession = Depends(get_db),
        teacher: Student = Depends(get_current_teacher),
):
    rows = (await db.execute(
        select(TeamProject)
        .where(TeamProject.teacher_id == teacher.id)
        .options(*_team_load_options())
        .order_by(TeamProject.created_at.desc())
    )).unique().scalars().all()
    return [_team_project_read(tp) for tp in rows]


# ── Student: my team-project ────────────────────────────────────────────────
@router.get("/my", response_model=list[MyTeamProjectRead])
async def my_team_projects(
        db: AsyncSession = Depends(get_db),
        student: Student = Depends(get_current_student),
):
    # Scoped to team projects this student actually belongs to (previously
    # fetched the WHOLE team_projects table and filtered in Python — a
    # platform-wide performance issue on top of the leak this also caused,
    # see _team_project_read_for_student above).
    team_project_ids = (await db.execute(
        select(TeamProjectTeam.team_project_id)
        .join(TeamProjectMember, TeamProjectMember.team_id == TeamProjectTeam.id)
        .where(TeamProjectMember.student_id == student.id)
        .distinct()
    )).scalars().all()
    if not team_project_ids:
        return []

    rows = (await db.execute(
        select(TeamProject)
        .where(TeamProject.id.in_(team_project_ids))
        .options(*_team_load_options())
    )).unique().scalars().all()

    out = []
    for tp in rows:
        team, membership = _find_team_and_membership(tp, student.id)
        if team is None:
            continue
        out.append(MyTeamProjectRead(
            team_project=_team_project_read_for_student(tp, team.id),
            my_team=_team_read(team),
            my_role=membership.role.value,
        ))
    return out


# ── Detail (teacher-only — students use /my, which redacts other teams) ────
@router.get("/{team_project_id}", response_model=TeamProjectRead)
async def get_assignment(
        team_project_id: int,
        db: AsyncSession = Depends(get_db),
        teacher: Student = Depends(get_current_teacher),
):
    tp = await _fetch_team_project(db, team_project_id)
    if tp.teacher_id != teacher.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    return _team_project_read(tp)


# ── Teacher: regenerate a team's plan ───────────────────────────────────────
@router.post("/teams/{team_id}/regenerate", response_model=TeamRead)
async def regenerate_team_plan(
        team_id: int,
        db: AsyncSession = Depends(get_db),
        teacher: Student = Depends(get_current_teacher),
):
    team = (await db.execute(
        select(TeamProjectTeam)
        .where(TeamProjectTeam.id == team_id)
        .options(selectinload(TeamProjectTeam.team_project))
    )).scalar_one_or_none()
    if team is None:
        raise HTTPException(status_code=404, detail="Jamoa topilmadi")
    if team.team_project.teacher_id != teacher.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    if team.generation_attempts >= MAX_GENERATION_ATTEMPTS:
        raise HTTPException(status_code=400, detail="Urinishlar soni tugadi (3/3)")

    # Clear previously-generated tasks before regenerating, so the old plan
    # doesn't sit alongside a new one.
    old_tasks = (await db.execute(
        select(TeamProjectTask).where(TeamProjectTask.team_id == team_id)
    )).scalars().all()
    for t in old_tasks:
        await db.delete(t)
    await db.flush()

    await generate_plan_for_team(db, team_id)

    tp = await _fetch_team_project(db, team.team_project_id)
    team_out = next(t for t in tp.teams if t.id == team_id)
    return _team_read(team_out)


# ── Student: submit a task ──────────────────────────────────────────────────
@router.post("/teams/{team_id}/tasks/{task_id}/submit", response_model=TaskRead)
async def submit_task(
        team_id: int, task_id: int, body: TaskSubmitBody,
        db: AsyncSession = Depends(get_db),
        student: Student = Depends(get_current_student),
):
    task = (await db.execute(
        select(TeamProjectTask).where(
            TeamProjectTask.id == task_id, TeamProjectTask.team_id == team_id,
        )
    )).scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Vazifa topilmadi")
    if task.assigned_student_id != student.id:
        raise HTTPException(status_code=403, detail="Bu vazifa sizga tegishli emas")
    if not body.submission_url and not body.submission_files:
        raise HTTPException(status_code=400, detail="Havola yoki fayl kerak")

    task.submission_url = body.submission_url
    task.submission_files = body.submission_files
    task.submitted_at = utcnow()
    task.status = TaskStatus.submitted
    await db.commit()

    await review_task_submission(db, task_id)
    # Same MissingGreenlet crash as reassign_task below, on the same
    # uncached task.assigned_student access inside _task_read — this is
    # the student-facing submit flow, so it's hit far more often.
    await db.refresh(task, attribute_names=["assigned_student"])
    return _task_read(task)


# ── Teacher: reassign a task ─────────────────────────────────────────────────
@router.post("/teams/{team_id}/tasks/{task_id}/reassign", response_model=TaskRead)
async def reassign_task(
        team_id: int, task_id: int, body: ReassignBody,
        db: AsyncSession = Depends(get_db),
        teacher: Student = Depends(get_current_teacher),
):
    # No ownership check existed at all here — any teacher account could
    # reassign any task on any team platform-wide. Found while reviewing
    # this endpoint, not reported; fixed given the severity, matching the
    # same check regenerate_team_plan already does correctly above.
    team = (await db.execute(
        select(TeamProjectTeam)
        .where(TeamProjectTeam.id == team_id)
        .options(selectinload(TeamProjectTeam.team_project))
    )).scalar_one_or_none()
    if team is None:
        raise HTTPException(status_code=404, detail="Jamoa topilmadi")
    if team.team_project.teacher_id != teacher.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    task = (await db.execute(
        select(TeamProjectTask).where(
            TeamProjectTask.id == task_id, TeamProjectTask.team_id == team_id,
        )
    )).scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Vazifa topilmadi")
    member = (await db.execute(
        select(TeamProjectMember).where(
            TeamProjectMember.team_id == team_id, TeamProjectMember.student_id == body.student_id,
        )
    )).scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=400, detail="Bu o'quvchi jamoa a'zosi emas")

    db.add(TeamProjectEvent(
        team_project_id=(await db.execute(
            select(TeamProjectTeam.team_project_id).where(TeamProjectTeam.id == team_id)
        )).scalar_one(),
        team_id=team_id, actor_student_id=teacher.id, event_type="task_reassigned",
        payload_json=json.dumps({"task_id": task_id, "to_student_id": body.student_id}),
    ))
    task.assigned_student_id = body.student_id
    task.status = TaskStatus.assigned
    task.submission_url = None
    task.submission_files = None
    task.submitted_at = None
    task.reviewed_at = None
    task.ai_score = None
    task.ai_feedback_json = None
    await db.commit()
    # db.refresh(task) only reloads scalar columns, not relationships —
    # _task_read accesses task.assigned_student, which crashes with
    # MissingGreenlet on the first un-cached access outside an explicit
    # async-aware load. Confirmed this is a real, reproducible 500 on
    # every actual call to this endpoint (not just a test artifact) while
    # writing the regression test for it.
    await db.refresh(task, attribute_names=["assigned_student"])
    return _task_read(task)


# ── Student (lead): finalize ─────────────────────────────────────────────────
@router.post("/teams/{team_id}/finalize", response_model=TeamRead)
async def finalize_team(
        team_id: int, body: FinalizeBody,
        db: AsyncSession = Depends(get_db),
        student: Student = Depends(get_current_student),
):
    team = (await db.execute(
        select(TeamProjectTeam)
        .where(TeamProjectTeam.id == team_id)
        .options(selectinload(TeamProjectTeam.tasks), selectinload(TeamProjectTeam.team_project))
        .with_for_update()
    )).scalar_one_or_none()
    if team is None:
        raise HTTPException(status_code=404, detail="Jamoa topilmadi")
    if team.lead_student_id != student.id:
        raise HTTPException(status_code=403, detail="Faqat jamoa integratori yakunlashi mumkin")
    # Without this, calling finalize twice (double-click, retry after a slow
    # response) creates a second Project row and silently overwrites
    # final_project_id — found while reviewing this endpoint, not reported.
    if team.status in (TeamStatus.submitted, TeamStatus.reviewed):
        raise HTTPException(status_code=409, detail="Jamoa allaqachon yakunlangan")
    if not team.tasks or any(t.status != TaskStatus.approved for t in team.tasks):
        raise HTTPException(status_code=400, detail="Barcha vazifalar tasdiqlanmagan")

    stack = TECH_STACKS_BY_KEY.get(team.tech_stack)
    technologies = [stack["frontend"], stack["backend"]] if stack else []

    project_service = ProjectService(db)
    project = await project_service.create_project(student.id, ProjectCreate(
        title=team.project_title or "Jamoaviy loyiha",
        description=body.description or team.project_description or "Jamoaviy loyiha yakuniy topshirig'i",
        github_url=body.github_url,
        live_demo_url=body.live_demo_url,
        technologies_used=technologies,
    ))
    await project_service.submit_project(project.id, student.id)

    team.final_project_id = project.id
    team.status = TeamStatus.submitted
    team.submitted_at = utcnow()
    db.add(TeamProjectEvent(
        team_project_id=team.team_project_id, team_id=team.id,
        actor_student_id=student.id, event_type="team_finalized",
        payload_json=json.dumps({"final_project_id": project.id}),
    ))
    await db.commit()

    # submit_project() runs the AI review SYNCHRONOUSLY — project.reviewed_at
    # is already set here if it succeeded (same session, same identity-mapped
    # object). Award points + mark the team reviewed now rather than via a
    # separate callback; if the AI was unavailable, the team just stays
    # "submitted" until someone re-triggers review through the normal
    # project flow — award_points only ever runs once reviewed_at is real.
    await db.refresh(project)
    if project.reviewed_at is not None:
        from app.services.team_project_points_service import award_points
        await award_points(db, team)
        team.status = TeamStatus.reviewed
        db.add(TeamProjectEvent(
            team_project_id=team.team_project_id, team_id=team.id,
            event_type="points_awarded",
            payload_json=json.dumps({"grade": project.grade}),
        ))
        await db.commit()

    tp = await _fetch_team_project(db, team.team_project_id)
    # A team can now reach "reviewed" directly (synchronous AI review,
    # above), not just "submitted" — the original check only matched the
    # latter, so a team project where every team finished instantly would
    # never have advanced tp.status past "active" at all.
    if all(t.status in (TeamStatus.submitted, TeamStatus.reviewed) for t in tp.teams):
        tp.status = (
            TeamProjectStatus.reviewed
            if all(t.status == TeamStatus.reviewed for t in tp.teams)
            else TeamProjectStatus.submitted
        )
        await db.commit()

    team_out = next(t for t in tp.teams if t.id == team_id)
    return _team_read(team_out)


# ── Student: peer ratings (after the team has submitted) ───────────────────
@router.post("/teams/{team_id}/peer-ratings", status_code=status.HTTP_204_NO_CONTENT)
async def submit_peer_ratings(
        team_id: int, body: list[PeerRatingItem],
        db: AsyncSession = Depends(get_db),
        student: Student = Depends(get_current_student),
):
    team = (await db.execute(
        select(TeamProjectTeam).where(TeamProjectTeam.id == team_id)
    )).scalar_one_or_none()
    if team is None:
        raise HTTPException(status_code=404, detail="Jamoa topilmadi")
    if team.status not in (TeamStatus.submitted, TeamStatus.reviewed):
        raise HTTPException(
            status_code=400, detail="Baholash faqat jamoa yakunlangandan keyin mumkin",
        )

    members = (await db.execute(
        select(TeamProjectMember).where(TeamProjectMember.team_id == team_id)
    )).scalars().all()
    member_ids = {m.student_id for m in members}
    if student.id not in member_ids:
        raise HTTPException(status_code=403, detail="Siz bu jamoa a'zosi emassiz")

    for item in body:
        if item.rated_student_id == student.id:
            raise HTTPException(status_code=400, detail="O'zingizni baholay olmaysiz")
        if item.rated_student_id not in member_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Student {item.rated_student_id} bu jamoa a'zosi emas",
            )

    for item in body:
        existing = (await db.execute(
            select(TeamProjectPeerRating).where(
                TeamProjectPeerRating.team_id == team_id,
                TeamProjectPeerRating.rater_student_id == student.id,
                TeamProjectPeerRating.rated_student_id == item.rated_student_id,
            )
        )).scalar_one_or_none()
        if existing is not None:
            # Allow updating a rating submitted before a deadline, rather
            # than erroring on resubmission — the spec doesn't say either
            # way, and failing a student who just wants to fix a typo in
            # their comment seems worse than a quiet overwrite.
            existing.score = item.score
            existing.comment = item.comment
        else:
            db.add(TeamProjectPeerRating(
                team_id=team_id, rater_student_id=student.id,
                rated_student_id=item.rated_student_id,
                score=item.score, comment=item.comment,
            ))
    await db.commit()
