"""Team-game session: core CRUD, lifecycle, and the realtime WebSocket.

Snapshot/summary/CSV-export/parent-bot-facing routes live in the sibling
team_game_session_reports.py — split out (2026-09-11) because this file had
grown to 1200+ lines mixing two genuinely separate concerns: running a live
session vs. reporting on a finished one. Shared session-loading/broadcast
helpers live in team_game_common.py so neither half imports from the other,
except this file's complete_session, which needs reports' snapshot-freezing
— see team_game_common.py's module docstring for why that's one-directional.
"""
import random
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select, text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.dependencies import get_db, get_current_teacher, get_current_student
from app.models.team_game import (
    GameSession, GameTeam, GameTeamMember, GameQuestion,
    SessionStatus, QuestionStatus, StudentQuestionOrder, GameType,
)
from app.models.user import Student
from app.schemas.team_game import (
    GameSessionRead, GameSessionCreate, StudentRead, ScoreUpdate, StartSessionBody,
)
from app.ws.manager import manager
from app.api.v1.endpoints.team_game_common import (
    TEAM_NAMES, load_session_options, course_title, my_auto_progress_map,
    question_count_map, build_session_read, fetch_session, fetch_and_build,
    broadcast_session, spawn_background_task,
)
from app.api.v1.endpoints.team_game_common import question_start_payload
from app.api.v1.endpoints.team_game_session_reports import _freeze_snapshot, _notify_parent_bot

router = APIRouter(redirect_slashes=False)


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
        read = await fetch_and_build(db, session_id, student_id=user_id)
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
    return await fetch_and_build(db, session.id)


# ── List sessions ──────────────────────────────────────────────────────────────
@router.get("/", response_model=List[GameSessionRead])
@router.get("", response_model=List[GameSessionRead])
async def list_sessions(
    course_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    from sqlalchemy import and_, or_
    from app.models.user import UserRole
    from app.models.course import student_courses
    from app.services.teacher_students import student_teacher_ids_subquery

    q = select(GameSession).options(*load_session_options()).order_by(GameSession.created_at.desc())
    if course_id:
        q = q.where(GameSession.course_id == course_id)
    is_teacher = current_student.role == UserRole.teacher
    if not is_teacher:
        # Students see only in-flight sessions — completed ones are noise
        # on their side. Teachers keep full history so the Завершённые
        # tab in the teacher UI can list them for post-game review.
        q = q.where(GameSession.status != SessionStatus.completed)
        # ...and only sessions they could actually end up on a team in:
        # either a course they're enrolled in, or a course-less session
        # created by a teacher who actually has them (via Group/Flow) —
        # NOT every course-less session platform-wide. A course-less game
        # used to be "open to everyone" regardless of who made it, so a
        # turon student who'd never met a given gennis teacher still saw
        # (and could join) that teacher's games. Mirrors start_session's
        # own fallback below, which now resolves the same way.
        enrolled_ids = select(student_courses.c.course_id).where(
            student_courses.c.student_id == current_student.id
        )
        my_teacher_ids = select(student_teacher_ids_subquery(current_student.id))
        q = q.where(
            or_(
                and_(GameSession.course_id.isnot(None), GameSession.course_id.in_(enrolled_ids)),
                and_(GameSession.course_id.is_(None), GameSession.created_by.in_(my_teacher_ids)),
            )
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
    progress_map = await my_auto_progress_map(db, auto_session_ids, sid)
    qcount_map = await question_count_map(db, [s.id for s in sessions])

    return [
        build_session_read(s, sid, titles.get(s.course_id), progress_map.get(s.id), qcount_map.get(s.id, 0))
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
        select(GameSession).where(GameSession.id == session_id).options(*load_session_options())
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
    ctitle = await course_title(db, session.course_id)
    progress_map = await my_auto_progress_map(db, [session_id], sid) if session.auto_mode else {}
    qcount_map = await question_count_map(db, [session_id])
    return build_session_read(session, sid, ctitle, progress_map.get(session_id), qcount_map.get(session_id, 0))


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
    from app.services.teacher_students import teacher_student_ids_subquery

    # Teacher's own groups' membership — used to label each student's group
    # in the response below. Kept Group-only (Flow has no equivalent "class"
    # label); scoping itself now goes through teacher_student_ids_subquery
    # just below, which also reaches students the teacher only has via a Flow.
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
        teacher_student_ids = select(teacher_student_ids_subquery(teacher.id))
        rows = (await db.execute(
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
        .options(*load_session_options())
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
        # No course, no explicit picks — used to fall back to literally
        # every active student on the platform, so a course-less game
        # silently pulled in other teachers' (including other systems')
        # students who'd never even met this teacher. Scope it to this
        # teacher's own students instead, same as get_session_students
        # above shows the teacher before they start it.
        from app.services.teacher_students import teacher_student_ids_subquery
        teacher_student_ids = select(teacher_student_ids_subquery(teacher.id))
        stu_res = await db.execute(
            select(Student)
            .where(
                Student.id.in_(teacher_student_ids),
                Student.role == UserRole.student,
                Student.is_active == True,
            )
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

    await broadcast_session(db, session_id)
    return await fetch_and_build(db, session_id)


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

    await broadcast_session(db, session_id)
    return await fetch_and_build(db, session_id)


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

    await broadcast_session(db, session_id)
    return await fetch_and_build(db, session_id)


# ── Teacher: complete session ──────────────────────────────────────────────────
@router.post("/{session_id}/complete", response_model=GameSessionRead)
async def complete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    result = await db.execute(
        select(GameSession).where(GameSession.id == session_id).options(*load_session_options())
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

    await broadcast_session(db, session_id)
    # Fire-and-forget: don't await, don't await the task — teacher must
    # not wait on a bot round-trip and must not see the endpoint fail
    # if the bot is offline. The bot pulls the full snapshot back from
    # /summary-public once it picks up this notification.
    spawn_background_task(_notify_parent_bot(session_id))
    return await fetch_and_build(db, session_id)


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
