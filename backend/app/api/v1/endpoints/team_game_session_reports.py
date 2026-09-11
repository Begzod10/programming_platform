"""Team-game session reporting: post-completion snapshot, teacher summary,
CSV export, and the parent-bot-facing secret-authenticated endpoints.

Split out of team_game_session.py (2026-09-11) — that file had grown to
1200+ lines mixing live-session CRUD/lifecycle with this genuinely separate
"report on a finished session" concern. See team_game_session.py's module
docstring for the shared-helper/import-direction rationale.

The two leading-underscore names here (_freeze_snapshot, _notify_parent_bot)
are imported directly by team_game_session.py's complete_session — kept the
underscore prefix from the original single-file version since they're still
package-internal, not part of this module's router-level API surface.
"""
import csv
import hmac
import io
import logging
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select, text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_db, get_current_teacher
from app.models.team_game import GameSession, GameQuestion, GameAnswer, SessionStatus
from app.models.game_session_snapshot import GameSessionSnapshot
from app.models.user import Student
from app.api.v1.endpoints.team_game_common import load_session_options, course_title

router = APIRouter(redirect_slashes=False)

_bot_logger = logging.getLogger("parent_bot_notify")


async def _build_snapshot_payload(db: AsyncSession, session_id: int) -> dict:
    """Produce the full immutable summary for a completed session.

    Reads live tables once, computes leaderboard + per-question stats +
    per-student per-question answers, and returns a JSON-serialisable
    dict. The caller writes this into game_session_snapshots.payload.
    """
    session_row = (await db.execute(
        select(GameSession).where(GameSession.id == session_id).options(*load_session_options())
    )).scalar_one_or_none()
    if session_row is None:
        raise HTTPException(status_code=404, detail="Session not found")

    ctitle = await course_title(db, session_row.course_id)

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
            "course_title": ctitle,
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


# ── Teacher: CSV export ───────────────────────────────────────────────────────
# BUG FIXED (2026-09-11, found while splitting this file out): this decorator
# used to sit directly above _csv_option_label — a private helper with an
# unrelated (q: dict, idx) signature, not a route handler — registering IT
# as the GET /{session_id}/export.csv endpoint instead of the actual handler
# below. session_export_csv had no decorator at all and was never reachable.
# Confirmed live-broken: GET .../export.csv resolved to _csv_option_label as
# its endpoint function (verified via app.routes before this fix landed).
@router.get("/{session_id}/export.csv")
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
