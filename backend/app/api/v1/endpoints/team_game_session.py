import asyncio
import csv
import hmac
import io
import logging
import random
from datetime import datetime, timezone
from typing import List, Optional

import httpx
from fastapi import APIRouter, Body, Depends, Header, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select, text as sa_text

from app.config import settings

_bot_logger = logging.getLogger("parent_bot_notify")

# asyncio only holds a *weak* reference to tasks created via create_task — if
# nothing else references the task object, it can be garbage-collected mid-flight
# before its await completes. Keep a strong reference here until it's done.
_background_tasks: set = set()


def _spawn_background_task(coro) -> None:
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, noload, load_only

from app.core.security import decode_access_token
from app.dependencies import get_db, get_current_teacher, get_current_student
from app.models.team_game import (
    GameSession, GameTeam, GameTeamMember, GameQuestion, GameAnswer,
    SessionStatus, QuestionStatus, StudentQuestionOrder, GameType,
)
from app.models.game_session_snapshot import GameSessionSnapshot
from app.models.user import Student
from app.schemas.team_game import (
    GameSessionRead, GameSessionCreate, GameTeamRead,
    TeamMemberRead, ScoreUpdate, StudentRead,
    StartSessionBody,
)
from app.ws.manager import manager
from app.api.v1.endpoints.team_game_common import question_start_payload

router = APIRouter(redirect_slashes=False)

TEAM_NAMES = [
    ("Alpha",   "#e74c3c"), ("Beta",    "#3498db"), ("Gamma",   "#2ecc71"),
    ("Delta",   "#f39c12"), ("Epsilon", "#9b59b6"), ("Zeta",    "#1abc9c"),
    ("Eta",     "#e67e22"), ("Theta",   "#e91e63"), ("Iota",    "#00bcd4"),
    ("Kappa",   "#8bc34a"),
]


def _load_opts():
    return [
        selectinload(GameSession.teams).selectinload(GameTeam.members).selectinload(
            GameTeamMember.student
        ).options(
            load_only(Student.id, Student.full_name, Student.username, Student.avatar_url)
        ),
        noload(GameSession.course),
        noload(GameSession.creator),
    ]


async def _course_title(db: AsyncSession, course_id: Optional[int]) -> Optional[str]:
    if not course_id:
        return None
    row = (await db.execute(sa_text("SELECT title FROM courses WHERE id = :id"), {"id": course_id})).first()
    return row[0] if row else None


async def _my_auto_progress_map(db: AsyncSession, session_ids: List[int],
                                 student_id: Optional[int]) -> dict:
    """For auto-mode sessions, map session_id -> (answered, total) for this student."""
    if not student_id or not session_ids:
        return {}
    totals = dict((await db.execute(
        select(GameQuestion.session_id, func.count(GameQuestion.id))
        .where(GameQuestion.session_id.in_(session_ids))
        .group_by(GameQuestion.session_id)
    )).all())
    if not totals:
        return {}
    answered = dict((await db.execute(
        select(GameQuestion.session_id, func.count(GameAnswer.id))
        .join(GameAnswer, GameAnswer.question_id == GameQuestion.id)
        .where(GameQuestion.session_id.in_(list(totals.keys())), GameAnswer.student_id == student_id)
        .group_by(GameQuestion.session_id)
    )).all())
    return {sid: (answered.get(sid, 0), total) for sid, total in totals.items()}


async def _question_count_map(db: AsyncSession, session_ids: List[int]) -> dict:
    """Count-only query (no row hydration) so the teacher list's "Вопросы (N)"
    tab has a real number without eager-loading every question's full text."""
    if not session_ids:
        return {}
    rows = (await db.execute(
        select(GameQuestion.session_id, func.count(GameQuestion.id))
        .where(GameQuestion.session_id.in_(session_ids))
        .group_by(GameQuestion.session_id)
    )).all()
    return dict(rows)


def _build_session_read(session: GameSession, student_id: Optional[int] = None,
                        course_title: Optional[str] = None,
                        my_auto_progress: Optional[tuple] = None,
                        questions_count: int = 0) -> GameSessionRead:
    my_team_id = None
    teams_out = []
    for team in session.teams:
        member_ids = {m.student_id for m in team.members}
        if student_id and student_id in member_ids:
            my_team_id = team.id
        members = [
            TeamMemberRead(
                id=m.id,
                student_id=m.student_id,
                full_name=getattr(m.student, "full_name", None) or getattr(m.student, "username", ""),
                username=getattr(m.student, "username", None),
                avatar_url=getattr(m.student, "avatar_url", None),
            )
            for m in team.members
        ]
        teams_out.append(GameTeamRead(id=team.id, name=team.name, color=team.color,
                                      score=team.score, members=members))
    teams_out.sort(key=lambda t: -t.score)

    my_auto_answered = my_auto_total = None
    my_auto_completed = None
    if my_auto_progress is not None:
        my_auto_answered, my_auto_total = my_auto_progress
        my_auto_completed = my_auto_total > 0 and my_auto_answered >= my_auto_total

    return GameSessionRead(
        id=session.id,
        title=session.title,
        description=session.description,
        game_type=session.game_type,
        status=session.status,
        auto_mode=session.auto_mode,
        course_id=session.course_id,
        course_title=course_title,
        created_by=session.created_by,
        team_count=session.team_count,
        teams=teams_out,
        created_at=session.created_at,
        updated_at=session.updated_at,
        my_team_id=my_team_id,
        my_auto_completed=my_auto_completed,
        my_auto_answered=my_auto_answered,
        my_auto_total=my_auto_total,
        questions_count=questions_count,
    )


async def _fetch_session(db: AsyncSession, session_id: int) -> GameSession:
    # populate_existing=True forces a refresh of already-identity-mapped relationships
    # (e.g. .teams) within the same request/transaction — without it, a handler that
    # mutates teams via raw db.add()/delete() (not through the ORM collection) and then
    # re-fetches in the same session would see the stale pre-mutation collection.
    result = await db.execute(
        select(GameSession)
        .where(GameSession.id == session_id)
        .options(*_load_opts())
        .execution_options(populate_existing=True)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    return session


async def _fetch_and_build(db: AsyncSession, session_id: int,
                           student_id: Optional[int] = None) -> GameSessionRead:
    session = await _fetch_session(db, session_id)
    ctitle  = await _course_title(db, session.course_id)
    progress_map = await _my_auto_progress_map(db, [session_id], student_id) if session.auto_mode else {}
    qcount_map = await _question_count_map(db, [session_id])
    return _build_session_read(session, student_id, ctitle, progress_map.get(session_id),
                                qcount_map.get(session_id, 0))


async def _broadcast_session(db: AsyncSession, session_id: int) -> None:
    read = await _fetch_and_build(db, session_id)
    await manager.broadcast(session_id, {"type": "session_update", "data": read.model_dump(mode="json")})


# ── WebSocket: real-time session updates ──────────────────────────────────────
@router.websocket("/{session_id}/ws")
async def session_ws(
    session_id: int,
    websocket: WebSocket,
    token: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    from app.models.user import UserRole
    from app.models.course import student_courses

    user_id = decode_access_token(token) if token else None
    if user_id is None:
        await websocket.close(code=4001)
        return

    user = (await db.execute(
        select(Student).where(Student.id == user_id)
    )).scalar_one_or_none()
    if not user or not user.is_active:
        await websocket.close(code=4001)
        return

    session = (await db.execute(
        select(GameSession).where(GameSession.id == session_id)
    )).scalar_one_or_none()
    if not session:
        await websocket.close(code=4004)
        return

    is_teacher = user.role == UserRole.teacher
    if is_teacher:
        if session.created_by != user.id:
            await websocket.close(code=4003)
            return
    elif session.course_id is not None:
        enrolled = (await db.execute(
            select(student_courses.c.course_id).where(
                student_courses.c.student_id == user.id,
                student_courses.c.course_id == session.course_id,
            )
        )).first()
        if not enrolled:
            await websocket.close(code=4003)
            return

    await manager.connect(session_id, websocket)
    try:
        read = await _fetch_and_build(db, session_id, student_id=user_id)
        await websocket.send_json({"type": "session_update", "data": read.model_dump(mode="json")})
        # If a question is already active, send question_start so late joiners/reconnects see it
        active_q_res = await db.execute(
            select(GameQuestion).where(
                GameQuestion.session_id == session_id,
                GameQuestion.status == QuestionStatus.active,
            )
        )
        active_q = active_q_res.scalar_one_or_none()
        if active_q:
            await websocket.send_json({
                "type": "question_start",
                "data": question_start_payload(active_q),
            })
    except Exception as exc:
        import logging as _logging
        _logging.getLogger(__name__).warning("ws init error session=%d: %s", session_id, exc)
        await websocket.close(code=1011)
        manager.disconnect(session_id, websocket)
        return

    try:
        while True:
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)


# ── Teacher: create session ────────────────────────────────────────────────────
@router.post("", response_model=GameSessionRead, status_code=status.HTTP_201_CREATED)
async def create_session(
    body: GameSessionCreate,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    session = GameSession(
        title=body.title,
        description=body.description,
        game_type=body.game_type,
        course_id=body.course_id,
        created_by=teacher.id,
        team_count=body.team_count,
        status=SessionStatus.pending,
    )
    db.add(session)
    await db.flush()

    # Individual games get one team per student at /start time — creating
    # placeholder teams here would just show a confusing "Team Alpha/Beta"
    # leaderboard before the session has even started.
    if body.game_type == GameType.team:
        names = TEAM_NAMES[:body.team_count]
        random.shuffle(names)
        for name, color in names:
            db.add(GameTeam(session_id=session.id, name=f"Team {name}", color=color))

    await db.commit()
    return await _fetch_and_build(db, session.id)


# ── List sessions ──────────────────────────────────────────────────────────────
@router.get("/", response_model=List[GameSessionRead])
@router.get("", response_model=List[GameSessionRead])
async def list_sessions(
    course_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    from app.models.user import UserRole
    from app.models.course import student_courses

    q = select(GameSession).options(*_load_opts()).order_by(GameSession.created_at.desc())
    if course_id:
        q = q.where(GameSession.course_id == course_id)
    is_teacher = current_student.role == UserRole.teacher
    if not is_teacher:
        # Students see only in-flight sessions — completed ones are noise
        # on their side. Teachers keep full history so the Завершённые
        # tab in the teacher UI can list them for post-game review.
        q = q.where(GameSession.status != SessionStatus.completed)
        # ...and only sessions for a course they're actually enrolled in, or
        # platform-wide sessions with no course_id (open to everyone, same
        # rule start_session already uses to assign teams to "all students"
        # when no course is set).
        enrolled_ids = select(student_courses.c.course_id).where(
            student_courses.c.student_id == current_student.id
        )
        q = q.where(
            (GameSession.course_id.is_(None)) | (GameSession.course_id.in_(enrolled_ids))
        )
    if is_teacher:
        # Teachers only see sessions they own — no reason to expose
        # other teachers' rooms in a shared list.
        q = q.where(GameSession.created_by == current_student.id)
    result = await db.execute(q)
    sessions = result.scalars().all()
    sid = current_student.id

    # Batch-fetch course titles to avoid N+1
    course_ids = list({s.course_id for s in sessions if s.course_id})
    titles: dict[int, str] = {}
    if course_ids:
        rows = (await db.execute(
            sa_text("SELECT id, title FROM courses WHERE id = ANY(:ids)"),
            {"ids": course_ids}
        )).all()
        titles = {r[0]: r[1] for r in rows}

    auto_session_ids = [s.id for s in sessions if s.auto_mode]
    progress_map = await _my_auto_progress_map(db, auto_session_ids, sid)
    qcount_map = await _question_count_map(db, [s.id for s in sessions])

    return [
        _build_session_read(s, sid, titles.get(s.course_id), progress_map.get(s.id), qcount_map.get(s.id, 0))
        for s in sessions
    ]


# ── Get single session ─────────────────────────────────────────────────────────
@router.get("/{session_id}", response_model=GameSessionRead)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    from app.models.user import UserRole
    from app.models.course import student_courses

    result = await db.execute(
        select(GameSession).where(GameSession.id == session_id).options(*_load_opts())
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    is_teacher = current_student.role == UserRole.teacher
    if is_teacher:
        if session.created_by != current_student.id:
            raise HTTPException(status_code=403, detail="Not your session")
    elif session.course_id is not None:
        enrolled = (await db.execute(
            select(student_courses.c.course_id).where(
                student_courses.c.student_id == current_student.id,
                student_courses.c.course_id == session.course_id,
            )
        )).first()
        if not enrolled:
            raise HTTPException(status_code=403, detail="Not enrolled in this session's course")

    sid    = current_student.id
    ctitle = await _course_title(db, session.course_id)
    progress_map = await _my_auto_progress_map(db, [session_id], sid) if session.auto_mode else {}
    qcount_map = await _question_count_map(db, [session_id])
    return _build_session_read(session, sid, ctitle, progress_map.get(session_id), qcount_map.get(session_id, 0))


# ── Teacher: list available students for a session ────────────────────────────
@router.get("/{session_id}/students", response_model=List[StudentRead])
async def get_session_students(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    session = (await db.execute(
        select(GameSession).where(GameSession.id == session_id)
    )).scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.created_by != teacher.id:
        raise HTTPException(status_code=403, detail="Not your session")

    from app.models.user import UserRole
    from app.models.group import Group, student_groups

    # Teacher's own groups' membership — used both to scope student-less-of-a-course
    # sessions to only this teacher's students, and to label each student's group.
    group_rows = (await db.execute(
        select(student_groups.c.student_id, Group.id, Group.name)
        .join(Group, Group.id == student_groups.c.group_id)
        .where(Group.teacher_id == teacher.id)
    )).all()
    # Keep only the first group per student (teachers may have one group per student)
    student_group_map = {}
    for sid, gid, gname in group_rows:
        if sid not in student_group_map:
            student_group_map[sid] = (gid, gname)

    if session.course_id:
        from app.models.course import student_courses
        rows = (await db.execute(
            select(Student)
            .join(student_courses, Student.id == student_courses.c.student_id)
            .where(
                student_courses.c.course_id == session.course_id,
                Student.role == UserRole.student,
                Student.is_active == True,
            )
            .distinct()
            .order_by(Student.full_name)
        )).scalars().all()
    else:
        teacher_student_ids = list(student_group_map.keys())
        rows = [] if not teacher_student_ids else (await db.execute(
            select(Student)
            .where(
                Student.id.in_(teacher_student_ids),
                Student.role == UserRole.student,
                Student.is_active == True,
            )
            .order_by(Student.full_name)
        )).scalars().all()

    return [
        StudentRead(
            id=s.id,
            full_name=s.full_name or None,
            username=s.username,
            avatar_url=s.avatar_url or None,
            group_id=student_group_map.get(s.id, (None, None))[0],
            group_name=student_group_map.get(s.id, (None, None))[1],
        )
        for s in rows
    ]


# ── Teacher: start session ─────────────────────────────────────────────────────
@router.post("/{session_id}/start", response_model=GameSessionRead)
async def start_session(
    session_id: int,
    body: Optional[StartSessionBody] = Body(default=None),
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    from app.models.team_game import GameType as GT
    result = await db.execute(
        select(GameSession)
        .where(GameSession.id == session_id)
        .with_for_update()
        .options(*_load_opts())
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.created_by != teacher.id:
        raise HTTPException(status_code=403, detail="Not your session")
    if session.status != SessionStatus.pending:
        raise HTTPException(status_code=400, detail="Session already started or completed")

    from app.models.user import UserRole

    # If teacher provided specific student_ids, use those; otherwise use all
    if body and body.student_ids:
        stu_res = await db.execute(
            select(Student)
            .where(Student.id.in_(body.student_ids), Student.role == UserRole.student, Student.is_active == True)
            .order_by(Student.full_name)
        )
        students = stu_res.scalars().all()
    elif session.course_id:
        from app.models.course import student_courses
        enroll_res = await db.execute(
            select(Student).distinct()
            .join(student_courses, Student.id == student_courses.c.student_id)
            .where(
                student_courses.c.course_id == session.course_id,
                Student.role == UserRole.student,
                Student.is_active == True,
            )
            .order_by(Student.full_name)
        )
        students = enroll_res.scalars().all()
    else:
        stu_res = await db.execute(
            select(Student)
            .where(Student.role == UserRole.student, Student.is_active == True)
            .order_by(Student.full_name)
        )
        students = stu_res.scalars().all()

    # Clear existing team members regardless of assignment method
    for team in session.teams:
        for m in list(team.members):
            await db.delete(m)
    await db.flush()

    if body and body.team_assignments:
        # Manual assignment: teacher explicitly assigned each student to a team
        session_team_ids = {t.id for t in session.teams}
        total_assigned = sum(len(ta.student_ids) for ta in body.team_assignments)
        if total_assigned == 0:
            raise HTTPException(status_code=400, detail="No students assigned to any team")
        for ta in body.team_assignments:
            if ta.team_id not in session_team_ids:
                raise HTTPException(status_code=400, detail=f"Team {ta.team_id} not found in session")
            for sid in ta.student_ids:
                db.add(GameTeamMember(team_id=ta.team_id, student_id=sid))
    else:
        if not students:
            raise HTTPException(status_code=400, detail="No students to assign")

        if session.game_type == GT.individual:
            # One team per student — delete placeholder teams first
            for team in list(session.teams):
                await db.delete(team)
            await db.flush()

            COLORS = ["#e74c3c","#3498db","#2ecc71","#f39c12","#9b59b6","#1abc9c",
                      "#e67e22","#e91e63","#00bcd4","#8bc34a"]
            for idx, stu in enumerate(students):
                name = (stu.full_name or stu.username or f"Студент {idx+1}")[:30]
                team = GameTeam(session_id=session_id, name=name, color=COLORS[idx % len(COLORS)])
                db.add(team)
                await db.flush()
                db.add(GameTeamMember(team_id=team.id, student_id=stu.id))
        else:
            # Team game: distribute randomly across existing teams
            student_ids = [s.id for s in students]
            random.shuffle(student_ids)
            teams = list(session.teams)
            for i, sid in enumerate(student_ids):
                db.add(GameTeamMember(team_id=teams[i % len(teams)].id, student_id=sid))

    session.status = SessionStatus.active
    await db.commit()

    await _broadcast_session(db, session_id)
    return await _fetch_and_build(db, session_id)


# ── Teacher: activate auto mode ───────────────────────────────────────────────
@router.post("/{session_id}/activate-auto", response_model=GameSessionRead)
async def activate_auto_mode(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    result = await db.execute(
        select(GameSession).where(GameSession.id == session_id).with_for_update()
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.created_by != teacher.id:
        raise HTTPException(status_code=403, detail="Not your session")
    if session.status != SessionStatus.active:
        raise HTTPException(status_code=400, detail="Session must be active before enabling auto mode")

    # Load all questions for this session
    questions = (await db.execute(
        select(GameQuestion)
        .where(GameQuestion.session_id == session_id)
        .order_by(GameQuestion.order_index)
    )).scalars().all()
    if not questions:
        raise HTTPException(status_code=400, detail="No questions in session — add questions first")

    q_ids = [q.id for q in questions]

    # Load all student IDs currently in this session via team members
    rows = (await db.execute(
        sa_text(
            "SELECT DISTINCT gtm.student_id FROM game_team_members gtm "
            "JOIN game_teams gt ON gt.id = gtm.team_id "
            "WHERE gt.session_id = :sid"
        ),
        {"sid": session_id}
    )).all()
    student_ids = [r[0] for r in rows]

    # Create or replace per-student shuffled question orders
    for sid in student_ids:
        shuffled = list(q_ids)
        random.shuffle(shuffled)
        existing = (await db.execute(
            select(StudentQuestionOrder).where(
                StudentQuestionOrder.session_id == session_id,
                StudentQuestionOrder.student_id == sid,
            )
        )).scalar_one_or_none()
        if existing:
            existing.question_ids = shuffled
        else:
            db.add(StudentQuestionOrder(session_id=session_id, student_id=sid, question_ids=shuffled))

    session.auto_mode = True
    await db.commit()

    await _broadcast_session(db, session_id)
    return await _fetch_and_build(db, session_id)


# ── Teacher: update score ──────────────────────────────────────────────────────
@router.patch("/{session_id}/score", response_model=GameSessionRead)
async def update_score(
    session_id: int,
    body: ScoreUpdate,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    # Light ownership check — no need to load all teams/members yet
    sess_row = (await db.execute(
        select(GameSession.id, GameSession.created_by)
        .where(GameSession.id == session_id)
    )).first()
    if not sess_row:
        raise HTTPException(status_code=404, detail="Session not found")
    if sess_row.created_by != teacher.id:
        raise HTTPException(status_code=403, detail="Not your session")

    team_row = (await db.execute(
        select(GameTeam.id)
        .where(GameTeam.id == body.team_id, GameTeam.session_id == session_id)
    )).first()
    if not team_row:
        raise HTTPException(status_code=404, detail="Team not found")

    # Atomic update — no lost-update race between concurrent requests
    await db.execute(
        sa_text(
            "UPDATE game_teams SET score = GREATEST(0, score + :delta) WHERE id = :team_id"
        ),
        {"delta": body.delta, "team_id": body.team_id},
    )
    await db.commit()

    await _broadcast_session(db, session_id)
    return await _fetch_and_build(db, session_id)


async def _build_snapshot_payload(db: AsyncSession, session_id: int) -> dict:
    """Produce the full immutable summary for a completed session.

    Reads live tables once, computes leaderboard + per-question stats +
    per-student per-question answers, and returns a JSON-serialisable
    dict. The caller writes this into game_session_snapshots.payload.
    """
    session_row = (await db.execute(
        select(GameSession).where(GameSession.id == session_id).options(*_load_opts())
    )).scalar_one_or_none()
    if session_row is None:
        raise HTTPException(status_code=404, detail="Session not found")

    course_title = await _course_title(db, session_row.course_id)

    q_rows = (await db.execute(
        select(GameQuestion)
        .where(GameQuestion.session_id == session_id)
        .order_by(GameQuestion.order_index)
    )).scalars().all()

    a_rows = (await db.execute(
        select(GameAnswer).where(
            GameAnswer.question_id.in_([q.id for q in q_rows]) if q_rows else sa_text("false")
        )
    )).scalars().all() if q_rows else []

    # Build a student directory for stable names in the exports.
    student_ids = {a.student_id for a in a_rows}
    for team in session_row.teams:
        for m in team.members:
            student_ids.add(m.student_id)
    students_by_id: dict = {}
    if student_ids:
        s_rows = (await db.execute(
            select(Student.id, Student.full_name, Student.username)
            .where(Student.id.in_(student_ids))
        )).all()
        students_by_id = {
            sid: {"id": sid, "full_name": full or username or f"#{sid}", "username": username}
            for sid, full, username in s_rows
        }

    team_by_student: dict = {}
    teams_out = []
    for team in session_row.teams:
        member_list = []
        for m in team.members:
            team_by_student[m.student_id] = {"id": team.id, "name": team.name, "color": team.color}
            info = students_by_id.get(m.student_id, {"id": m.student_id, "full_name": f"#{m.student_id}"})
            member_list.append({
                "student_id": m.student_id,
                "full_name": info["full_name"],
                "username": info.get("username"),
            })
        teams_out.append({
            "id": team.id, "name": team.name, "color": team.color,
            "score": team.score, "members": member_list,
        })
    teams_out.sort(key=lambda t: -t["score"])

    # Per-question aggregates + per-student per-question rows.
    answers_by_question: dict = {}
    for a in a_rows:
        answers_by_question.setdefault(a.question_id, []).append(a)

    questions_out = []
    for q in q_rows:
        answers = answers_by_question.get(q.id, [])
        opt_count = len(q.options or [])
        option_counts = [0] * opt_count
        for a in answers:
            if 0 <= a.chosen_option < opt_count:
                option_counts[a.chosen_option] += 1
        correct_count = sum(1 for a in answers if a.is_correct)
        questions_out.append({
            "id": q.id,
            "order_index": q.order_index,
            "question_text": q.question_text,
            "question_text_ru": q.question_text_ru,
            "options": q.options,
            "options_ru": q.options_ru,
            "correct_option": q.correct_option,
            "points": q.points,
            "time_limit": q.time_limit,
            "activated_at": q.activated_at.isoformat() if q.activated_at else None,
            "question_kind": q.question_kind,
            "code_snippet": q.code_snippet,
            "code_language": q.code_language,
            "bug_line": q.bug_line,
            "bug_explanation": q.bug_explanation,
            "bug_explanation_ru": q.bug_explanation_ru,
            "stats": {
                "total_answers": len(answers),
                "correct_answers": correct_count,
                "wrong_answers": len(answers) - correct_count,
                "option_counts": option_counts,
            },
        })

    # Per-student summary (leaderboard rows) computed from answers.
    per_student: dict = {}
    for a in a_rows:
        row = per_student.setdefault(a.student_id, {
            "student_id": a.student_id,
            "correct_count": 0,
            "wrong_count": 0,
            "answered_count": 0,
            "total_points": 0,
        })
        row["answered_count"] += 1
        row["total_points"] += a.points_earned or 0
        if a.is_correct:
            row["correct_count"] += 1
        else:
            row["wrong_count"] += 1
    # Deliberately DO NOT pad the leaderboard with team members who never
    # answered. In "individual" sessions especially, the members set can
    # be everyone in the teacher's groups (dozens of rows) so padding
    # made the summary a wall of zeros. If a UI needs "who was
    # registered but skipped", it can diff against the teams array.
    leaderboard = []
    for sid, row in per_student.items():
        info = students_by_id.get(sid, {"id": sid, "full_name": f"#{sid}"})
        team = team_by_student.get(sid)
        leaderboard.append({
            **row,
            "full_name": info["full_name"],
            "username": info.get("username"),
            "team_id": team["id"] if team else None,
            "team_name": team["name"] if team else None,
            "team_color": team["color"] if team else None,
        })
    leaderboard.sort(key=lambda r: (-r["total_points"], -r["correct_count"], r["full_name"]))
    for rank, row in enumerate(leaderboard, start=1):
        row["rank"] = rank

    # Per-student per-question answer detail (for CSV export).
    answer_rows = []
    for a in a_rows:
        info = students_by_id.get(a.student_id, {"id": a.student_id, "full_name": f"#{a.student_id}"})
        answer_rows.append({
            "question_id": a.question_id,
            "student_id": a.student_id,
            "student_name": info["full_name"],
            "team_id": a.team_id,
            "chosen_option": a.chosen_option,
            "is_correct": a.is_correct,
            "points_earned": a.points_earned,
            "answered_at": a.answered_at.isoformat() if a.answered_at else None,
        })

    return {
        "session": {
            "id": session_row.id,
            "title": session_row.title,
            "description": session_row.description,
            "game_type": session_row.game_type,
            "auto_mode": session_row.auto_mode,
            "language": session_row.language,
            "team_count": session_row.team_count,
            "course_id": session_row.course_id,
            "course_title": course_title,
            "created_by": session_row.created_by,
            "created_at": session_row.created_at.isoformat() if session_row.created_at else None,
        },
        "teams": teams_out,
        "questions": questions_out,
        "leaderboard": leaderboard,
        "answers": answer_rows,
        "totals": {
            "questions": len(questions_out),
            "participants": len(leaderboard),
            "total_answers": len(a_rows),
        },
    }


async def _notify_parent_bot(session_id: int) -> None:
    """Fire-and-forget POST to gennis_parent_bot's internal trigger.

    The bot is on the same box, so this is a localhost call. Any failure
    (bot down, misconfig, network) is swallowed and logged — completing
    a game session must never depend on the bot being alive.
    """
    url = (settings.PARENT_BOT_URL or "").rstrip("/")
    secret = settings.PARENT_BOT_SECRET
    if not url or not secret:
        return
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f"{url}/internal/game-session-complete",
                json={"session_id": session_id},
                headers={"X-Internal-Secret": secret},
            )
    except Exception as exc:
        _bot_logger.warning("parent-bot notify failed session=%d: %s", session_id, exc)


async def _freeze_snapshot(
    db: AsyncSession, session_id: int, completed_by: Optional[int],
) -> None:
    """Insert one game_session_snapshots row for this session.

    Idempotent — if a snapshot already exists (teacher re-clicks
    Завершить, or completion path fires twice), keep the earlier one
    rather than overwriting the historical record.
    """
    existing = (await db.execute(
        select(GameSessionSnapshot.id).where(GameSessionSnapshot.session_id == session_id)
    )).scalar_one_or_none()
    if existing is not None:
        return
    payload = await _build_snapshot_payload(db, session_id)
    db.add(GameSessionSnapshot(
        session_id=session_id,
        completed_by=completed_by,
        payload=payload,
    ))
    await db.flush()


# ── Teacher: complete session ──────────────────────────────────────────────────
@router.post("/{session_id}/complete", response_model=GameSessionRead)
async def complete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    result = await db.execute(
        select(GameSession).where(GameSession.id == session_id).options(*_load_opts())
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.created_by != teacher.id:
        raise HTTPException(status_code=403, detail="Not your session")

    await db.execute(
        sa_text(
            "UPDATE game_questions SET status = 'revealed' "
            "WHERE session_id = :sid AND status = 'active'"
        ),
        {"sid": session_id}
    )
    session.status = SessionStatus.completed
    await _freeze_snapshot(db, session_id, completed_by=teacher.id)
    await db.commit()

    await _broadcast_session(db, session_id)
    # Fire-and-forget: don't await, don't await the task — teacher must
    # not wait on a bot round-trip and must not see the endpoint fail
    # if the bot is offline. The bot pulls the full snapshot back from
    # /summary-public once it picks up this notification.
    _spawn_background_task(_notify_parent_bot(session_id))
    return await _fetch_and_build(db, session_id)


async def _get_snapshot_for_teacher(
    db: AsyncSession, session_id: int, teacher_id: int,
) -> GameSessionSnapshot:
    """Load a snapshot, enforcing teacher ownership.

    Also handles the transitional case where a session was completed
    before this table existed — falls back to writing the snapshot on
    read so the teacher can immediately view legacy sessions.
    """
    session_row = (await db.execute(
        select(GameSession).where(GameSession.id == session_id)
    )).scalar_one_or_none()
    if session_row is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if session_row.created_by != teacher_id:
        raise HTTPException(status_code=403, detail="Not your session")

    snap = (await db.execute(
        select(GameSessionSnapshot).where(GameSessionSnapshot.session_id == session_id)
    )).scalar_one_or_none()
    if snap is not None:
        return snap
    if session_row.status != SessionStatus.completed:
        raise HTTPException(
            status_code=409,
            detail="Session is not completed yet; no snapshot available",
        )
    await _freeze_snapshot(db, session_id, completed_by=teacher_id)
    await db.commit()
    snap = (await db.execute(
        select(GameSessionSnapshot).where(GameSessionSnapshot.session_id == session_id)
    )).scalar_one_or_none()
    if snap is None:
        raise HTTPException(status_code=500, detail="Failed to build snapshot")
    return snap


# ── Teacher: session summary (post-completion read-only) ──────────────────────
@router.get("/{session_id}/summary")
async def session_summary(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    snap = await _get_snapshot_for_teacher(db, session_id, teacher.id)
    return {
        "session_id": snap.session_id,
        "completed_at": snap.completed_at.isoformat() if snap.completed_at else None,
        "completed_by": snap.completed_by,
        **snap.payload,
    }


# ── Teacher: CSV export ───────────────────────────────────────────────────────
@router.get("/{session_id}/export.csv")
def _csv_option_label(q: dict, idx) -> str:
    """Render an option index as CSV text. For bug-hunt questions, `options`
    holds bare line numbers ("7") — labeling them "line 7" instead of
    dumping a bare digit next to the quiz questions' real answer text."""
    options = q.get("options") or []
    if not isinstance(idx, int) or not (0 <= idx < len(options)):
        return ""
    text = options[idx]
    return f"line {text}" if q.get("question_kind") == "bug_hunt" else text


def _csv_safe_row(row: list) -> list:
    """Prefix any cell that starts with a formula-trigger character (=, +, -, @)
    or a leading tab/CR with an apostrophe, so student/teacher-supplied text
    (full_name, team names, question text) can't execute as a formula or
    launch a link when a teacher opens this export in Excel/Sheets."""
    safe = []
    for v in row:
        if isinstance(v, str) and v and v[0] in ("=", "+", "-", "@", "\t", "\r"):
            safe.append("'" + v)
        else:
            safe.append(v)
    return safe


async def session_export_csv(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    snap = await _get_snapshot_for_teacher(db, session_id, teacher.id)
    payload = snap.payload
    buf = io.StringIO()
    # BOM so Excel opens it as UTF-8 by default (student names contain Cyrillic).
    buf.write("﻿")
    w = csv.writer(buf)

    session_meta = payload.get("session", {})
    w.writerow(_csv_safe_row(["Session", session_meta.get("title", ""), f"id={session_meta.get('id')}"]))
    w.writerow(["Completed at", snap.completed_at.isoformat() if snap.completed_at else ""])
    w.writerow(["Game type", session_meta.get("game_type", "")])
    w.writerow(_csv_safe_row(["Course", session_meta.get("course_title") or ""]))
    w.writerow([])

    w.writerow(["=== LEADERBOARD ==="])
    w.writerow(["Rank", "Student", "Team", "Points", "Correct", "Wrong", "Answered"])
    for row in payload.get("leaderboard", []):
        w.writerow(_csv_safe_row([
            row.get("rank"),
            row.get("full_name", ""),
            row.get("team_name") or "",
            row.get("total_points", 0),
            row.get("correct_count", 0),
            row.get("wrong_count", 0),
            row.get("answered_count", 0),
        ]))
    w.writerow([])

    w.writerow(["=== QUESTIONS ==="])
    w.writerow(["#", "Question", "Correct option", "Total answers", "Correct", "Wrong", "Option counts", "Explanation"])
    for q in payload.get("questions", []):
        options = q.get("options") or []
        stats = q.get("stats", {})
        w.writerow(_csv_safe_row([
            q.get("order_index", 0) + 1,
            q.get("question_text", ""),
            _csv_option_label(q, q.get("correct_option")),
            stats.get("total_answers", 0),
            stats.get("correct_answers", 0),
            stats.get("wrong_answers", 0),
            " / ".join(f"{opt}: {cnt}" for opt, cnt in zip(options, stats.get("option_counts", []))),
            q.get("bug_explanation") or "",
        ]))
    w.writerow([])

    w.writerow(["=== PER-STUDENT ANSWERS ==="])
    w.writerow(["Student", "Question #", "Question", "Chosen", "Correct?", "Points", "Answered at"])
    q_by_id = {q["id"]: q for q in payload.get("questions", [])}
    for a in payload.get("answers", []):
        q = q_by_id.get(a.get("question_id")) or {}
        chosen_text = _csv_option_label(q, a.get("chosen_option"))
        w.writerow(_csv_safe_row([
            a.get("student_name", ""),
            (q.get("order_index", 0) + 1) if q else "",
            q.get("question_text", "") if q else "",
            chosen_text,
            "✓" if a.get("is_correct") else "✗",
            a.get("points_earned", 0),
            a.get("answered_at", ""),
        ]))

    buf.seek(0)
    filename = f"session-{session_id}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Bot: public secret-authenticated snapshot read ───────────────────────────
# The parent-bot service pulls session data via these endpoints. Auth is a
# plain shared secret (X-Internal-Secret header) — the bot doesn't have a
# JWT and shouldn't need one for read-only reporting queries.

def _require_internal_secret(x_internal_secret: Optional[str]) -> None:
    expected = settings.PARENT_BOT_SECRET
    if not expected:
        raise HTTPException(status_code=503, detail="Parent bot integration not configured")
    if not x_internal_secret or not hmac.compare_digest(x_internal_secret, expected):
        raise HTTPException(status_code=401, detail="Invalid internal secret")


@router.get("/{session_id}/summary-public")
async def session_summary_public(
    session_id: int,
    x_internal_secret: Optional[str] = Header(default=None, alias="X-Internal-Secret"),
    db: AsyncSession = Depends(get_db),
):
    _require_internal_secret(x_internal_secret)
    session_row = (await db.execute(
        select(GameSession).where(GameSession.id == session_id)
    )).scalar_one_or_none()
    if session_row is None:
        raise HTTPException(status_code=404, detail="Session not found")
    snap = (await db.execute(
        select(GameSessionSnapshot).where(GameSessionSnapshot.session_id == session_id)
    )).scalar_one_or_none()
    if snap is None:
        if session_row.status != SessionStatus.completed:
            raise HTTPException(
                status_code=409,
                detail="Session is not completed yet; no snapshot available",
            )
        await _freeze_snapshot(db, session_id, completed_by=None)
        await db.commit()
        snap = (await db.execute(
            select(GameSessionSnapshot).where(GameSessionSnapshot.session_id == session_id)
        )).scalar_one_or_none()
    return {
        "session_id": snap.session_id,
        "completed_at": snap.completed_at.isoformat() if snap.completed_at else None,
        "completed_by": snap.completed_by,
        **snap.payload,
    }


@router.get("/completed-today")
async def sessions_completed_today(
    x_internal_secret: Optional[str] = Header(default=None, alias="X-Internal-Secret"),
    db: AsyncSession = Depends(get_db),
):
    """Session IDs that got their snapshot within the last 24 hours.

    Used by the parent bot's daily 20:00 rollup task — the bot iterates
    these IDs, fetches each summary via /summary-public, and rolls the
    per-student sections into one message per parent.
    """
    _require_internal_secret(x_internal_secret)
    # 24-hour window rather than "since midnight" so the 20:00 job
    # doesn't miss a session completed at 20:05 the previous day.
    since = datetime.now(timezone.utc).replace(microsecond=0)
    since_expr = sa_text("now() - interval '24 hours'")
    rows = (await db.execute(
        select(GameSessionSnapshot.session_id, GameSessionSnapshot.completed_at)
        .where(GameSessionSnapshot.completed_at >= since_expr)
        .order_by(GameSessionSnapshot.completed_at)
    )).all()
    return {
        "sessions": [
            {"session_id": sid, "completed_at": ca.isoformat() if ca else None}
            for sid, ca in rows
        ],
    }


# ── Teacher: delete session ────────────────────────────────────────────────────
@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    result = await db.execute(select(GameSession).where(GameSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.created_by != teacher.id:
        raise HTTPException(status_code=403, detail="Not your session")
    await db.delete(session)
    await db.commit()
    await manager.broadcast(session_id, {"type": "session_deleted"})
