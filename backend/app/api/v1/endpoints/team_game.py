import random
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select, text as sa_text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, noload, load_only

from app.core.security import decode_access_token
from app.dependencies import get_db, get_current_teacher, get_current_student_optional, get_current_student
from app.models.team_game import GameSession, GameTeam, GameTeamMember, GameQuestion, GameAnswer, SessionStatus, QuestionStatus
from app.models.lesson_question import LessonQuestion
from app.models.user import Student
from app.schemas.team_game import (
    GameSessionRead, GameSessionCreate, GameTeamRead,
    TeamMemberRead, ScoreUpdate, StudentRead,
    StartSessionBody, GameQuestionCreate, GameQuestionRead,
    AnswerSubmit, AnswerResultRead, QuestionEndPayload,
)
from app.ws.manager import manager

router = APIRouter()

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
            .order_by(Student.full_name)
        )).scalars().all()
    else:
        rows = (await db.execute(
            select(Student)
            .where(Student.role == UserRole.student, Student.is_active == True)
            .order_by(Student.full_name)
        )).scalars().all()

    return [
        StudentRead(
            id=s.id,
            full_name=s.full_name or None,
            username=s.username,
            avatar_url=s.avatar_url or None,
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

    for team in session.teams:
        for m in list(team.members):
            await db.delete(m)
    await db.flush()

    if body and body.assignments:
        # Manual assignment supplied by teacher
        team_ids = {t.id for t in session.teams}
        for item in body.assignments:
            if item.team_id not in team_ids:
                raise HTTPException(status_code=400, detail=f"Team {item.team_id} not in this session")
            for sid in item.student_ids:
                db.add(GameTeamMember(team_id=item.team_id, student_id=sid))
    else:
        # Random assignment fallback
        from app.models.user import UserRole
        if session.course_id:
            from app.models.course import student_courses
            enroll_res = await db.execute(
                select(student_courses.c.student_id)
                .join(Student, Student.id == student_courses.c.student_id)
                .where(
                    student_courses.c.course_id == session.course_id,
                    Student.role == UserRole.student,
                    Student.is_active == True,
                )
            )
            student_ids = [r[0] for r in enroll_res.all()]
        else:
            stu_res = await db.execute(
                select(Student.id).where(Student.role == UserRole.student, Student.is_active == True)
            )
            student_ids = [r[0] for r in stu_res.all()]

        if not student_ids:
            raise HTTPException(status_code=400, detail="No students to assign")

        random.shuffle(student_ids)
        teams = list(session.teams)
        for i, sid in enumerate(student_ids):
            db.add(GameTeamMember(team_id=teams[i % len(teams)].id, student_id=sid))

    session.status = SessionStatus.active
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


# ═══════════════════════════════════════════════════════════════════════════════
# Quiz question endpoints
# ═══════════════════════════════════════════════════════════════════════════════

async def _get_teacher_session(db: AsyncSession, session_id: int, teacher_id: int) -> GameSession:
    sess = (await db.execute(select(GameSession).where(GameSession.id == session_id))).scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    if sess.created_by != teacher_id:
        raise HTTPException(status_code=403, detail="Not your session")
    return sess


# ── Teacher: add question ──────────────────────────────────────────────────────
@router.post("/{session_id}/questions", response_model=GameQuestionRead, status_code=status.HTTP_201_CREATED)
async def add_question(
    session_id: int,
    body: GameQuestionCreate,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    sess = await _get_teacher_session(db, session_id, teacher.id)
    if sess.status == SessionStatus.completed:
        raise HTTPException(status_code=400, detail="Cannot add questions to a completed session")

    # Auto-assign order_index if not provided
    count_row = (await db.execute(
        sa_text("SELECT COUNT(*) FROM game_questions WHERE session_id = :sid"),
        {"sid": session_id}
    )).scalar()
    order = body.order_index if body.order_index is not None else int(count_row or 0)

    q = GameQuestion(
        session_id=session_id,
        question_text=body.question_text,
        options=body.options,
        correct_option=body.correct_option,
        time_limit=body.time_limit,
        points=body.points,
        order_index=order,
        status=QuestionStatus.pending,
    )
    db.add(q)
    await db.commit()
    await db.refresh(q)
    return q


# ── Teacher: list questions ────────────────────────────────────────────────────
@router.get("/{session_id}/questions", response_model=List[GameQuestionRead])
async def list_questions(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    await _get_teacher_session(db, session_id, teacher.id)
    rows = (await db.execute(
        select(GameQuestion)
        .where(GameQuestion.session_id == session_id)
        .order_by(GameQuestion.order_index)
    )).scalars().all()
    return rows


# ── Teacher: delete question ───────────────────────────────────────────────────
@router.delete("/{session_id}/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    session_id: int,
    question_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    await _get_teacher_session(db, session_id, teacher.id)
    q = (await db.execute(
        select(GameQuestion).where(GameQuestion.id == question_id, GameQuestion.session_id == session_id)
    )).scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    await db.delete(q)
    await db.commit()


# ── Teacher: activate a question (broadcast to students) ──────────────────────
@router.post("/{session_id}/questions/{question_id}/activate", response_model=GameQuestionRead)
async def activate_question(
    session_id: int,
    question_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    await _get_teacher_session(db, session_id, teacher.id)

    # Mark any currently active question as revealed first
    await db.execute(
        sa_text(
            "UPDATE game_questions SET status = 'revealed' "
            "WHERE session_id = :sid AND status = 'active'"
        ),
        {"sid": session_id}
    )

    q = (await db.execute(
        select(GameQuestion).where(GameQuestion.id == question_id, GameQuestion.session_id == session_id)
    )).scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    q.status = QuestionStatus.active
    q.activated_at = datetime.now(timezone.utc)

    await db.execute(
        sa_text("UPDATE game_sessions SET current_question_id = :qid WHERE id = :sid"),
        {"qid": question_id, "sid": session_id}
    )
    await db.commit()
    await db.refresh(q)

    # Broadcast question to students (WITHOUT correct_option)
    await manager.broadcast(session_id, {
        "type": "question_start",
        "data": {
            "id": q.id,
            "question_text": q.question_text,
            "options": q.options,
            "time_limit": q.time_limit,
            "points": q.points,
            "order_index": q.order_index,
            "activated_at": q.activated_at.isoformat(),
        }
    })
    return q


# ── Teacher: reveal answer ─────────────────────────────────────────────────────
@router.post("/{session_id}/questions/{question_id}/reveal")
async def reveal_question(
    session_id: int,
    question_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    await _get_teacher_session(db, session_id, teacher.id)

    q = (await db.execute(
        select(GameQuestion)
        .where(GameQuestion.id == question_id, GameQuestion.session_id == session_id)
        .options(selectinload(GameQuestion.answers).selectinload(GameAnswer.student))
    )).scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    if q.status != QuestionStatus.active:
        raise HTTPException(status_code=400, detail="Can only reveal an active question")

    q.status = QuestionStatus.revealed
    await db.commit()
    await db.refresh(q)

    # Build answer list
    answers_out = [
        AnswerResultRead(
            student_id=a.student_id,
            full_name=getattr(a.student, "full_name", None),
            team_id=a.team_id,
            chosen_option=a.chosen_option,
            is_correct=a.is_correct,
            points_earned=a.points_earned,
        )
        for a in q.answers
    ]

    # Current team scores
    teams = (await db.execute(
        select(GameTeam).where(GameTeam.session_id == session_id).order_by(GameTeam.score.desc())
    )).scalars().all()
    team_scores = [{"team_id": t.id, "name": t.name, "color": t.color, "score": t.score} for t in teams]

    payload = QuestionEndPayload(
        question_id=q.id,
        correct_option=q.correct_option,
        answers=answers_out,
        team_scores=team_scores,
    )
    await manager.broadcast(session_id, {"type": "question_end", "data": payload.model_dump()})
    return payload


# ── Student: submit answer ─────────────────────────────────────────────────────
@router.post("/{session_id}/questions/{question_id}/answer", response_model=AnswerResultRead)
async def submit_answer(
    session_id: int,
    question_id: int,
    body: AnswerSubmit,
    db: AsyncSession = Depends(get_db),
    student: Student = Depends(get_current_student),
):
    # Verify question is active
    q = (await db.execute(
        select(GameQuestion).where(
            GameQuestion.id == question_id,
            GameQuestion.session_id == session_id,
            GameQuestion.status == QuestionStatus.active,
        )
    )).scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=400, detail="Question is not active")

    # Find student's team
    member = (await db.execute(
        select(GameTeamMember)
        .join(GameTeam, GameTeam.id == GameTeamMember.team_id)
        .where(GameTeam.session_id == session_id, GameTeamMember.student_id == student.id)
    )).scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=400, detail="You are not assigned to a team in this session")

    # Check for duplicate answer
    existing = (await db.execute(
        select(GameAnswer).where(
            GameAnswer.question_id == question_id,
            GameAnswer.student_id == student.id,
        )
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Already answered")

    is_correct = body.chosen_option == q.correct_option

    # Time-based scoring: full points at 0s, 50% at time_limit, linear decay.
    # Answers submitted after the time limit are rejected entirely.
    points_earned = 0
    if is_correct and q.activated_at:
        now = datetime.now(timezone.utc)
        elapsed = (now - q.activated_at).total_seconds()
        if q.time_limit and q.time_limit > 0:
            if elapsed > q.time_limit:
                raise HTTPException(status_code=400, detail="Time limit for this question has expired")
            ratio = max(0.0, min(1.0, elapsed / q.time_limit))
            points_earned = max(int(q.points * (1.0 - ratio * 0.5)), int(q.points * 0.5))
        else:
            points_earned = q.points

    answer = GameAnswer(
        question_id=question_id,
        student_id=student.id,
        team_id=member.team_id,
        chosen_option=body.chosen_option,
        is_correct=is_correct,
        points_earned=points_earned,
    )
    db.add(answer)

    if is_correct and points_earned > 0:
        await db.execute(
            sa_text("UPDATE game_teams SET score = score + :pts WHERE id = :tid"),
            {"pts": points_earned, "tid": member.team_id},
        )

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Already answered")

    # Broadcast answer progress (count only, not who answered what)
    total_members = (await db.execute(
        sa_text(
            "SELECT COUNT(*) FROM game_team_members gtm "
            "JOIN game_teams gt ON gt.id = gtm.team_id "
            "WHERE gt.session_id = :sid"
        ),
        {"sid": session_id}
    )).scalar() or 0

    answered_count = (await db.execute(
        sa_text("SELECT COUNT(*) FROM game_answers WHERE question_id = :qid"),
        {"qid": question_id}
    )).scalar() or 0

    await manager.broadcast(session_id, {
        "type": "question_progress",
        "data": {
            "question_id": question_id,
            "answered_count": int(answered_count),
            "total_players": int(total_members),
        }
    })

    return AnswerResultRead(
        student_id=student.id,
        full_name=student.full_name,
        team_id=member.team_id,
        chosen_option=body.chosen_option,
        is_correct=is_correct,
        points_earned=points_earned,
    )


# ── Teacher: import questions from lesson / course question bank ───────────────
@router.post("/{session_id}/import-questions", response_model=List[GameQuestionRead])
async def import_questions_from_lesson(
    session_id: int,
    lesson_id: Optional[int] = None,
    course_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    teacher: Student = Depends(get_current_teacher),
):
    if not lesson_id and not course_id:
        raise HTTPException(status_code=400, detail="Provide lesson_id or course_id")

    sess = (await db.execute(select(GameSession).where(GameSession.id == session_id))).scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    if sess.created_by != teacher.id:
        raise HTTPException(status_code=403, detail="Not your session")

    if lesson_id:
        source_qs = (await db.execute(
            select(LessonQuestion)
            .where(LessonQuestion.lesson_id == lesson_id)
            .order_by(LessonQuestion.order_index, LessonQuestion.id)
        )).scalars().all()
    else:
        from app.models.lesson import Lesson as LessonModel
        lesson_ids_row = (await db.execute(
            select(LessonModel.id).where(LessonModel.course_id == course_id).order_by(LessonModel.order)
        )).scalars().all()
        source_qs = (await db.execute(
            select(LessonQuestion)
            .where(LessonQuestion.lesson_id.in_(lesson_ids_row))
            .order_by(LessonQuestion.lesson_id, LessonQuestion.order_index)
        )).scalars().all()

    if not source_qs:
        raise HTTPException(status_code=404, detail="No questions found for this lesson/course")

    # Get current max order_index in game session
    max_order = (await db.execute(
        sa_text("SELECT COALESCE(MAX(order_index), -1) FROM game_questions WHERE session_id = :sid"),
        {"sid": session_id}
    )).scalar()

    created = []
    for i, lq in enumerate(source_qs):
        gq = GameQuestion(
            session_id=session_id,
            question_text=lq.question_text,
            options=lq.options,
            correct_option=lq.correct_option,
            time_limit=lq.time_limit,
            points=lq.points,
            order_index=int(max_order) + 1 + i,
            status=QuestionStatus.pending,
        )
        db.add(gq)
        created.append(gq)

    await db.commit()
    for gq in created:
        await db.refresh(gq)

    return created
