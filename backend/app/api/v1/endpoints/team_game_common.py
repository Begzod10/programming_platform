"""Shared helpers between team_game_session.py, team_game_session_reports.py,
and team_game_questions.py.

Kept in its own module (rather than one endpoint file importing from
another) so team_game_session.py (core CRUD/lifecycle/WS routes) and
team_game_session_reports.py (snapshot/summary/CSV-export/bot-facing
routes) can share the same session-loading/broadcasting helpers without
either importing from the other — the only direct dependency between
those two is team_game_session.py's complete_session importing
_freeze_snapshot from the reports module, which stays one-directional.
"""
import asyncio
from typing import List, Optional

from sqlalchemy import func, select, text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, noload, load_only

from app.models.team_game import GameSession, GameTeam, GameTeamMember, GameQuestion, GameAnswer
from app.models.user import Student
from app.schemas.team_game import GameSessionRead, GameTeamRead, TeamMemberRead
from app.ws.manager import manager
from fastapi import HTTPException

TEAM_NAMES = [
    ("Alpha",   "#e74c3c"), ("Beta",    "#3498db"), ("Gamma",   "#2ecc71"),
    ("Delta",   "#f39c12"), ("Epsilon", "#9b59b6"), ("Zeta",    "#1abc9c"),
    ("Eta",     "#e67e22"), ("Theta",   "#e91e63"), ("Iota",    "#00bcd4"),
    ("Kappa",   "#8bc34a"),
]

# asyncio only holds a *weak* reference to tasks created via create_task — if
# nothing else references the task object, it can be garbage-collected mid-flight
# before its await completes. Keep a strong reference here until it's done.
_background_tasks: set = set()


def spawn_background_task(coro) -> None:
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


def load_session_options():
    return [
        selectinload(GameSession.teams).selectinload(GameTeam.members).selectinload(
            GameTeamMember.student
        ).options(
            load_only(Student.id, Student.full_name, Student.username, Student.avatar_url)
        ),
        noload(GameSession.course),
        noload(GameSession.creator),
    ]


async def course_title(db: AsyncSession, course_id: Optional[int]) -> Optional[str]:
    if not course_id:
        return None
    row = (await db.execute(sa_text("SELECT title FROM courses WHERE id = :id"), {"id": course_id})).first()
    return row[0] if row else None


async def my_auto_progress_map(db: AsyncSession, session_ids: List[int],
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


async def question_count_map(db: AsyncSession, session_ids: List[int]) -> dict:
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


def build_session_read(session: GameSession, student_id: Optional[int] = None,
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


async def fetch_session(db: AsyncSession, session_id: int) -> GameSession:
    # populate_existing=True forces a refresh of already-identity-mapped relationships
    # (e.g. .teams) within the same request/transaction — without it, a handler that
    # mutates teams via raw db.add()/delete() (not through the ORM collection) and then
    # re-fetches in the same session would see the stale pre-mutation collection.
    result = await db.execute(
        select(GameSession)
        .where(GameSession.id == session_id)
        .options(*load_session_options())
        .execution_options(populate_existing=True)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    return session


async def fetch_and_build(db: AsyncSession, session_id: int,
                           student_id: Optional[int] = None) -> GameSessionRead:
    session = await fetch_session(db, session_id)
    ctitle  = await course_title(db, session.course_id)
    progress_map = await my_auto_progress_map(db, [session_id], student_id) if session.auto_mode else {}
    qcount_map = await question_count_map(db, [session_id])
    return build_session_read(session, student_id, ctitle, progress_map.get(session_id),
                                qcount_map.get(session_id, 0))


async def broadcast_session(db: AsyncSession, session_id: int) -> None:
    read = await fetch_and_build(db, session_id)
    await manager.broadcast(session_id, {"type": "session_update", "data": read.model_dump(mode="json")})


def question_start_payload(q) -> dict:
    """Build the question_start WS payload for a GameQuestion.

    Used both when a teacher activates a question (broadcast to everyone)
    and when a student's WS reconnects mid-question (late-joiner catch-up)
    — those two call sites had drifted into two separately hand-written
    dict literals before this extraction.

    SECURITY: must never include the answer (bug_line, bug_explanation,
    bug_explanation_ru, or correct_option) — a student could read it out of
    devtools before the timer runs. Same discipline this payload already
    applied to correct_option; extend it to the new bug-hunt fields.
    """
    return {
        "id": q.id,
        "question_text": q.question_text,
        "question_text_ru": q.question_text_ru,
        "options": q.options,
        "time_limit": q.time_limit,
        "points": q.points,
        "order_index": q.order_index,
        "activated_at": q.activated_at.isoformat() if q.activated_at else None,
        "question_kind": q.question_kind,
        "code_snippet": q.code_snippet,
        "code_language": q.code_language,
    }
