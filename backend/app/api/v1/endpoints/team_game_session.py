import random
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select, text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, noload, load_only

from app.core.security import decode_access_token
from app.dependencies import get_db, get_current_teacher, get_current_student_optional
from app.models.team_game import (
    GameSession, GameTeam, GameTeamMember, GameQuestion,
    SessionStatus, QuestionStatus, StudentQuestionOrder,
)
from app.models.user import Student
from app.schemas.team_game import (
    GameSessionRead, GameSessionCreate, GameTeamRead,
    TeamMemberRead, ScoreUpdate, StudentRead,
    StartSessionBody,
)
from app.ws.manager import manager

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


def _build_session_read(session: GameSession, student_id: Optional[int] = None,
                        course_title: Optional[str] = None) -> GameSessionRead:
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
    )


async def _fetch_session(db: AsyncSession, session_id: int) -> GameSession:
    result = await db.execute(
        select(GameSession).where(GameSession.id == session_id).options(*_load_opts())
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    return session


async def _fetch_and_build(db: AsyncSession, session_id: int,
                           student_id: Optional[int] = None) -> GameSessionRead:
    session = await _fetch_session(db, session_id)
    ctitle  = await _course_title(db, session.course_id)
    return _build_session_read(session, student_id, ctitle)


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
    user_id = decode_access_token(token) if token else None
    if user_id is None:
        await websocket.close(code=4001)
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
                "data": {
                    "id": active_q.id,
                    "question_text": active_q.question_text,
                    "question_text_ru": active_q.question_text_ru,
                    "options": active_q.options,
                    "time_limit": active_q.time_limit,
                    "points": active_q.points,
                    "order_index": active_q.order_index,
                    "activated_at": active_q.activated_at.isoformat() if active_q.activated_at else None,
                },
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
    current_student: Optional[Student] = Depends(get_current_student_optional),
):
    q = select(GameSession).options(*_load_opts()).order_by(GameSession.created_at.desc())
    if course_id:
        q = q.where(GameSession.course_id == course_id)
    if current_student:
        q = q.where(GameSession.status != SessionStatus.completed)
    result = await db.execute(q)
    sessions = result.scalars().all()
    sid = current_student.id if current_student else None

    # Batch-fetch course titles to avoid N+1
    course_ids = list({s.course_id for s in sessions if s.course_id})
    titles: dict[int, str] = {}
    if course_ids:
        rows = (await db.execute(
            sa_text("SELECT id, title FROM courses WHERE id = ANY(:ids)"),
            {"ids": course_ids}
        )).all()
        titles = {r[0]: r[1] for r in rows}

    return [_build_session_read(s, sid, titles.get(s.course_id)) for s in sessions]


# ── Get single session ─────────────────────────────────────────────────────────
@router.get("/{session_id}", response_model=GameSessionRead)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_student: Optional[Student] = Depends(get_current_student_optional),
):
    result = await db.execute(
        select(GameSession).where(GameSession.id == session_id).options(*_load_opts())
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    sid    = current_student.id if current_student else None
    ctitle = await _course_title(db, session.course_id)
    return _build_session_read(session, sid, ctitle)


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
        rows = (await db.execute(
            select(Student)
            .where(Student.role == UserRole.student, Student.is_active == True)
            .order_by(Student.full_name)
        )).scalars().all()

    # Fetch teacher's group membership for each student in one query
    from app.models.group import Group, student_groups
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
    await db.commit()

    await _broadcast_session(db, session_id)
    return await _fetch_and_build(db, session_id)


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
