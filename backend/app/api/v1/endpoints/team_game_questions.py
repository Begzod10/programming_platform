import random
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text as sa_text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_db, get_current_teacher, get_current_student
from app.models.team_game import (
    GameSession, GameTeam, GameTeamMember, GameQuestion, GameAnswer,
    SessionStatus, QuestionStatus, StudentQuestionOrder,
)
from app.models.lesson_question import LessonQuestion
from app.models.user import Student
from app.schemas.team_game import (
    GameQuestionCreate, GameQuestionRead,
    AnswerSubmit, AnswerResultRead, QuestionEndPayload,
    AutoQuestionRead, AutoAnswerResultRead, AutoRankingEntry,
)
from app.ws.manager import manager

router = APIRouter(redirect_slashes=False)


async def _build_rankings(db: AsyncSession, session_id: int) -> List[AutoRankingEntry]:
    """Current standings for a session, highest score first.

    In individual mode each GameTeam is one student (team.name is already
    the student's display name), so this doubles as a live per-student
    ranking with no extra join needed.
    """
    teams = (await db.execute(
        select(GameTeam).where(GameTeam.session_id == session_id).order_by(GameTeam.score.desc())
    )).scalars().all()
    return [AutoRankingEntry(id=t.id, name=t.name, color=t.color, score=t.score) for t in teams]


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
            "question_text_ru": q.question_text_ru,
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

    # Find student's team (limit 1 guards against corrupt duplicate rows)
    member = (await db.execute(
        select(GameTeamMember)
        .join(GameTeam, GameTeam.id == GameTeamMember.team_id)
        .where(GameTeam.session_id == session_id, GameTeamMember.student_id == student.id)
        .limit(1)
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


# ── Student: get personal shuffled question list (auto mode) ──────────────────
@router.get("/{session_id}/my-questions", response_model=List[AutoQuestionRead])
async def get_my_questions(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    student: Student = Depends(get_current_student),
):
    sess = (await db.execute(select(GameSession).where(GameSession.id == session_id))).scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    if not sess.auto_mode:
        raise HTTPException(status_code=400, detail="Session is not in auto mode")
    if sess.status != SessionStatus.active:
        raise HTTPException(status_code=400, detail="Session is not active")

    # Verify student is a participant
    member = (await db.execute(
        select(GameTeamMember)
        .join(GameTeam, GameTeam.id == GameTeamMember.team_id)
        .where(GameTeam.session_id == session_id, GameTeamMember.student_id == student.id)
        .limit(1)
    )).scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=403, detail="You are not a participant in this session")

    # Get or create question order for this student
    order = (await db.execute(
        select(StudentQuestionOrder).where(
            StudentQuestionOrder.session_id == session_id,
            StudentQuestionOrder.student_id == student.id,
        )
    )).scalar_one_or_none()

    all_questions = (await db.execute(
        select(GameQuestion).where(GameQuestion.session_id == session_id)
    )).scalars().all()

    if not order:
        q_ids = [q.id for q in all_questions]
        random.shuffle(q_ids)
        order = StudentQuestionOrder(session_id=session_id, student_id=student.id, question_ids=q_ids)
        db.add(order)
        await db.commit()
    else:
        # Sync in any questions the teacher added after this student's order was
        # first created (e.g. mid-game) — append them so the student isn't stuck
        # with a stale, incomplete list from before they joined or started.
        existing_ids = set(order.question_ids)
        new_ids = [q.id for q in all_questions if q.id not in existing_ids]
        if new_ids:
            random.shuffle(new_ids)
            order.question_ids = order.question_ids + new_ids
            await db.commit()

    q_map = {q.id: q for q in all_questions}
    return [q_map[qid] for qid in order.question_ids if qid in q_map]


# ── Student: submit answer in auto mode ───────────────────────────────────────
@router.post("/{session_id}/questions/{question_id}/answer-auto", response_model=AutoAnswerResultRead)
async def submit_answer_auto(
    session_id: int,
    question_id: int,
    body: AnswerSubmit,
    db: AsyncSession = Depends(get_db),
    student: Student = Depends(get_current_student),
):
    sess = (await db.execute(select(GameSession).where(GameSession.id == session_id))).scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    if not sess.auto_mode:
        raise HTTPException(status_code=400, detail="Session is not in auto mode")

    q = (await db.execute(
        select(GameQuestion).where(
            GameQuestion.id == question_id,
            GameQuestion.session_id == session_id,
        )
    )).scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    # Find student's team
    member = (await db.execute(
        select(GameTeamMember)
        .join(GameTeam, GameTeam.id == GameTeamMember.team_id)
        .where(GameTeam.session_id == session_id, GameTeamMember.student_id == student.id)
        .limit(1)
    )).scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=403, detail="You are not a participant in this session")

    # Already answered (e.g. student refreshed mid-result or reopened the game
    # before their local question index advanced) — replay their original
    # result instead of erroring, so the client doesn't get stuck on this
    # question with no way to move on.
    existing = (await db.execute(
        select(GameAnswer).where(
            GameAnswer.question_id == question_id,
            GameAnswer.student_id == student.id,
        )
    )).scalar_one_or_none()
    if existing:
        return AutoAnswerResultRead(
            student_id=student.id,
            chosen_option=existing.chosen_option,
            correct_option=q.correct_option,
            is_correct=existing.is_correct,
            points_earned=existing.points_earned,
            my_team_id=member.team_id,
            rankings=await _build_rankings(db, session_id),
        )

    is_correct = body.chosen_option == q.correct_option
    points_earned = q.points if is_correct else 0

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

    rankings = await _build_rankings(db, session_id)

    # Broadcast live score update for teacher leaderboard
    if is_correct:
        await manager.broadcast(session_id, {
            "type": "auto_score_update",
            "data": {
                "team_scores": [
                    {"team_id": r.id, "name": r.name, "color": r.color, "score": r.score} for r in rankings
                ]
            }
        })

    return AutoAnswerResultRead(
        student_id=student.id,
        chosen_option=body.chosen_option,
        correct_option=q.correct_option,
        is_correct=is_correct,
        points_earned=points_earned,
        my_team_id=member.team_id,
        rankings=rankings,
    )


# ── Teacher: import questions from lesson / course question bank ───────────────
def _detect_lang(text: str) -> str:
    """Return 'ru' if text contains Cyrillic characters, else 'uz'."""
    return 'ru' if any('Ѐ' <= c <= 'ӿ' for c in text) else 'uz'


def _shuffle_permutation(length: int, correct_option: int):
    """Build a random permutation of indices; return (order, new_correct_option_index).

    `order[new_idx] = old_idx` — apply with _apply_permutation to reorder any
    parallel options list (e.g. UZ and RU variants) consistently.
    """
    order = list(range(length))
    random.shuffle(order)
    old_to_new = {old_idx: new_idx for new_idx, old_idx in enumerate(order)}
    return order, old_to_new[correct_option]


def _apply_permutation(options: list, order: list) -> list:
    return [options[old_idx] for old_idx in order]


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

    # Split by language and pair UZ+RU by position so students see both
    uz_qs = sorted([lq for lq in source_qs if _detect_lang(lq.question_text) == 'uz'], key=lambda x: (x.order_index, x.id))
    ru_qs = sorted([lq for lq in source_qs if _detect_lang(lq.question_text) == 'ru'], key=lambda x: (x.order_index, x.id))

    if not uz_qs and not ru_qs:
        raise HTTPException(status_code=404, detail="No questions found for this lesson/course")

    count = max(len(uz_qs), len(ru_qs))

    # Get current max order_index in game session
    max_order = (await db.execute(
        sa_text("SELECT COALESCE(MAX(order_index), -1) FROM game_questions WHERE session_id = :sid"),
        {"sid": session_id}
    )).scalar()

    created = []
    for i in range(count):
        uz_lq = uz_qs[i] if i < len(uz_qs) else None
        ru_lq = ru_qs[i] if i < len(ru_qs) else None
        base = uz_lq or ru_lq
        order, shuffled_correct = _shuffle_permutation(len(base.options), base.correct_option)
        shuffled_opts = _apply_permutation(base.options, order)

        # Only carry RU option variants when the paired RU question has the same
        # option count — otherwise the index-aligned permutation can't be applied
        # safely, so we drop options_ru rather than mismatch it against options.
        shuffled_opts_ru = None
        if uz_lq and ru_lq and len(ru_lq.options) == len(uz_lq.options):
            shuffled_opts_ru = _apply_permutation(ru_lq.options, order)

        gq = GameQuestion(
            session_id=session_id,
            question_text=uz_lq.question_text if uz_lq else ru_lq.question_text,
            question_text_ru=ru_lq.question_text if ru_lq else None,
            options=shuffled_opts,
            options_ru=shuffled_opts_ru,
            correct_option=shuffled_correct,
            time_limit=base.time_limit,
            points=base.points,
            order_index=int(max_order) + 1 + i,
            status=QuestionStatus.pending,
        )
        db.add(gq)
        created.append(gq)

    await db.commit()
    for gq in created:
        await db.refresh(gq)

    return created
