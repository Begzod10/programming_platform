"""Practice statistics — buckets, leeches, history, stats, sessions-overview, breakdown."""
from __future__ import annotations

from datetime import datetime, timedelta, date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, cast, Date, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_student
from app.models.course import Course
from app.models.dictionary import PracticeSession, UserDictionary
from app.models.lesson import Lesson
from app.models.user import Student
from app.services import srs
from .practice_words import _apply_scope
from .practice_session import _session_dict

router = APIRouter()


@router.get("/buckets")
async def get_retention_buckets(
    category_id: Optional[int] = Query(default=None),
    course_id: Optional[int] = Query(default=None),
    lesson_id: Optional[int] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    label = srs.bucket_expr(UserDictionary).label("bucket")
    stmt = _apply_scope(
        select(label, func.count().label("n"))
        .where(UserDictionary.student_id == current_user.id),
        category_id=category_id,
        course_id=course_id,
        lesson_id=lesson_id,
    ).group_by(label)
    rows = (await db.execute(stmt)).all()
    out = {"fragile": 0, "learning": 0, "solid": 0, "mastered": 0}
    for bucket, n in rows:
        out[bucket] = n
    return out


@router.get("/leeches")
async def get_leeches(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    rows = (
        await db.execute(
            select(UserDictionary)
            .where(
                UserDictionary.student_id == current_user.id,
                UserDictionary.lapses >= srs.LEECH_LAPSES,
            )
            .order_by(UserDictionary.lapses.desc(), UserDictionary.ease_factor.asc())
            .limit(limit)
        )
    ).scalars().all()
    return [
        {
            "id": w.id,
            "word": w.word,
            "context": w.context,
            "lapses": w.lapses,
            "ease_factor": w.ease_factor,
            "interval_days": w.interval_days,
        }
        for w in rows
    ]


@router.get("/history")
async def get_history(
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    rows = (
        await db.execute(
            select(PracticeSession)
            .where(
                PracticeSession.student_id == current_user.id,
                PracticeSession.completed_at.isnot(None),
            )
            .order_by(PracticeSession.started_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return [_session_dict(s) for s in rows]


def _compute_streaks(dates: List[date], today: date) -> tuple[int, int]:
    if not dates:
        return 0, 0
    days = sorted(set(dates), reverse=True)

    current = 0
    if days[0] == today:
        expected = today
    elif days[0] == today - timedelta(days=1):
        expected = today - timedelta(days=1)
    else:
        current = 0
        expected = None

    if expected is not None:
        for d in days:
            if d == expected:
                current += 1
                expected = expected - timedelta(days=1)
            else:
                break

    asc = sorted(set(dates))
    longest = 1
    run = 1
    for i in range(1, len(asc)):
        if asc[i] - asc[i - 1] == timedelta(days=1):
            run += 1
            longest = max(longest, run)
        else:
            run = 1
    return current, longest


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    now = datetime.utcnow()
    today = now.date()
    seven_ago_dt = datetime(today.year, today.month, today.day) - timedelta(days=6)

    date_rows = (
        await db.execute(
            select(cast(PracticeSession.completed_at, Date).label("d"))
            .where(PracticeSession.student_id == current_user.id, PracticeSession.completed_at.isnot(None))
            .group_by("d")
        )
    ).all()
    dates = [r[0] for r in date_rows if r[0] is not None]
    current_streak, longest_streak = _compute_streaks(dates, today)

    seven_rows = (
        await db.execute(
            select(
                cast(PracticeSession.completed_at, Date).label("d"),
                func.count(PracticeSession.id).label("sessions"),
                func.coalesce(func.sum(PracticeSession.total_words), 0).label("words"),
                func.coalesce(func.sum(PracticeSession.correct), 0).label("correct"),
            )
            .where(
                PracticeSession.student_id == current_user.id,
                PracticeSession.completed_at.isnot(None),
                PracticeSession.completed_at >= seven_ago_dt,
            )
            .group_by("d")
        )
    ).all()
    by_date = {r.d: r for r in seven_rows}
    last_7_days = []
    for i in range(7):
        d = today - timedelta(days=6 - i)
        row = by_date.get(d)
        words = int(row.words) if row else 0
        correct = int(row.correct) if row else 0
        last_7_days.append({
            "date": d.isoformat(),
            "sessions": int(row.sessions) if row else 0,
            "words": words,
            "correct": correct,
            "accuracy": round((correct / words) * 100) if words else 0,
        })

    mode_rows = (
        await db.execute(
            select(
                PracticeSession.mode,
                func.count(PracticeSession.id).label("sessions"),
                func.coalesce(func.sum(PracticeSession.total_words), 0).label("words"),
                func.coalesce(func.sum(PracticeSession.correct), 0).label("correct"),
            )
            .where(PracticeSession.student_id == current_user.id, PracticeSession.completed_at.isnot(None))
            .group_by(PracticeSession.mode)
        )
    ).all()
    mode_breakdown = []
    for r in mode_rows:
        words = int(r.words)
        correct = int(r.correct)
        mode_breakdown.append({
            "mode": r.mode,
            "sessions": int(r.sessions),
            "words": words,
            "correct": correct,
            "accuracy": round((correct / words) * 100) if words else 0,
        })
    mode_breakdown.sort(key=lambda x: x["sessions"], reverse=True)

    total_words = (
        await db.execute(
            select(func.count(UserDictionary.id)).where(UserDictionary.student_id == current_user.id)
        )
    ).scalar() or 0

    mastered = (
        await db.execute(
            select(func.count(UserDictionary.id)).where(
                UserDictionary.student_id == current_user.id,
                UserDictionary.interval_days > srs.SOLID_MAX_INT,
                ~srs.is_fragile(UserDictionary),
            )
        )
    ).scalar() or 0

    total_sessions = sum(r["sessions"] for r in mode_breakdown)
    total_drilled = sum(r["words"] for r in mode_breakdown)
    total_correct = sum(r["correct"] for r in mode_breakdown)
    overall_acc = round((total_correct / total_drilled) * 100) if total_drilled else 0

    return {
        "streak": {
            "current": current_streak,
            "longest": longest_streak,
            "today_practised": today in by_date,
        },
        "last_7_days": last_7_days,
        "mode_breakdown": mode_breakdown,
        "totals": {
            "words": total_words,
            "mastered": mastered,
            "mastery_pct": round((mastered / total_words) * 100) if total_words else 0,
            "sessions": total_sessions,
            "drilled": total_drilled,
            "accuracy": overall_acc,
        },
    }


@router.get("/sessions-overview")
async def get_sessions_overview(
    days: int = Query(default=30, ge=7, le=180),
    months: int = Query(default=6, ge=3, le=24),
    recent_limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    now = datetime.utcnow()
    today = now.date()
    day_window_start = datetime(today.year, today.month, today.day) - timedelta(days=days - 1)

    anchor_month = today.month - (months - 1)
    anchor_year = today.year
    while anchor_month <= 0:
        anchor_month += 12
        anchor_year -= 1
    month_window_start = datetime(anchor_year, anchor_month, 1)

    base_filter = [
        PracticeSession.student_id == current_user.id,
        PracticeSession.completed_at.isnot(None),
    ]

    day_rows = (
        await db.execute(
            select(
                cast(PracticeSession.completed_at, Date).label("d"),
                func.count(PracticeSession.id).label("sessions"),
                func.coalesce(func.sum(PracticeSession.total_words), 0).label("words"),
                func.coalesce(func.sum(PracticeSession.correct), 0).label("correct"),
            )
            .where(*base_filter, PracticeSession.completed_at >= day_window_start)
            .group_by("d")
        )
    ).all()
    by_day_map = {r.d: r for r in day_rows}
    by_date = []
    for i in range(days):
        d = today - timedelta(days=days - 1 - i)
        row = by_day_map.get(d)
        words = int(row.words) if row else 0
        correct = int(row.correct) if row else 0
        by_date.append({
            "date": d.isoformat(),
            "sessions": int(row.sessions) if row else 0,
            "words": words,
            "correct": correct,
            "accuracy": round((correct / words) * 100) if words else 0,
        })

    month_session_rows = (
        await db.execute(
            select(PracticeSession.completed_at, PracticeSession.total_words, PracticeSession.correct)
            .where(*base_filter, PracticeSession.completed_at >= month_window_start)
        )
    ).all()

    by_month_map: dict[str, dict] = {}
    cur_y, cur_m = anchor_year, anchor_month
    while True:
        key = f"{cur_y:04d}-{cur_m:02d}"
        by_month_map[key] = {"month": key, "sessions": 0, "words": 0, "correct": 0, "active_days": set()}
        if cur_y == today.year and cur_m == today.month:
            break
        cur_m += 1
        if cur_m > 12:
            cur_m = 1
            cur_y += 1

    for row in month_session_rows:
        ts: datetime = row.completed_at
        key = f"{ts.year:04d}-{ts.month:02d}"
        if key not in by_month_map:
            continue
        bucket = by_month_map[key]
        bucket["sessions"] += 1
        bucket["words"] += int(row.total_words or 0)
        bucket["correct"] += int(row.correct or 0)
        bucket["active_days"].add(ts.date())

    by_month = []
    for key in sorted(by_month_map.keys()):
        b = by_month_map[key]
        words = b["words"]
        correct = b["correct"]
        by_month.append({
            "month": key,
            "sessions": b["sessions"],
            "words": words,
            "correct": correct,
            "accuracy": round((correct / words) * 100) if words else 0,
            "active_days": len(b["active_days"]),
        })

    totals_row = (
        await db.execute(
            select(
                func.count(PracticeSession.id).label("sessions"),
                func.coalesce(func.sum(PracticeSession.total_words), 0).label("words"),
                func.coalesce(func.sum(PracticeSession.correct), 0).label("correct"),
                func.min(PracticeSession.started_at).label("first"),
            )
            .where(*base_filter)
        )
    ).first()

    sessions_total = int(totals_row.sessions or 0)
    words_total = int(totals_row.words or 0)
    correct_total = int(totals_row.correct or 0)
    first_seen: Optional[datetime] = totals_row.first

    duration_rows = (
        await db.execute(
            select(PracticeSession.started_at, PracticeSession.completed_at)
            .where(*base_filter, PracticeSession.started_at.isnot(None))
        )
    ).all()
    total_seconds = 0
    duration_samples = 0
    for r in duration_rows:
        if r.started_at and r.completed_at and r.completed_at > r.started_at:
            delta = (r.completed_at - r.started_at).total_seconds()
            if 5 <= delta <= 3600:
                total_seconds += delta
                duration_samples += 1

    avg_session_minutes = round(total_seconds / duration_samples / 60, 1) if duration_samples else 0
    avg_session_words = round(words_total / sessions_total, 1) if sessions_total else 0
    avg_session_accuracy = round((correct_total / words_total) * 100) if words_total else 0

    active_days_lifetime = (
        await db.execute(
            select(func.count(func.distinct(cast(PracticeSession.completed_at, Date)))).where(*base_filter)
        )
    ).scalar() or 0

    active_days_window = sum(1 for d in by_date if d["sessions"] > 0)

    if first_seen:
        weeks_active = max(1.0, (now - first_seen).total_seconds() / (7 * 86400))
        sessions_per_week = round(sessions_total / weeks_active, 1)
    else:
        sessions_per_week = 0

    recent_rows = (
        await db.execute(
            select(PracticeSession)
            .where(*base_filter)
            .order_by(PracticeSession.started_at.desc())
            .limit(recent_limit)
        )
    ).scalars().all()
    recent_sessions = []
    for s in recent_rows:
        duration_s = None
        if s.started_at and s.completed_at and s.completed_at > s.started_at:
            duration_s = int((s.completed_at - s.started_at).total_seconds())
        accuracy = round((s.correct / s.total_words) * 100) if s.total_words else 0
        recent_sessions.append({
            "id": s.id,
            "mode": s.mode,
            "total_words": s.total_words,
            "correct": s.correct,
            "accuracy": accuracy,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            "duration_seconds": duration_s,
        })

    return {
        "window": {
            "days": days,
            "months": months,
            "from_date": by_date[0]["date"] if by_date else None,
            "to_date": by_date[-1]["date"] if by_date else None,
        },
        "totals": {
            "sessions": sessions_total,
            "words": words_total,
            "correct": correct_total,
            "accuracy": avg_session_accuracy,
            "active_days": int(active_days_lifetime),
            "minutes": round(total_seconds / 60) if total_seconds else 0,
        },
        "averages": {
            "per_session_words": avg_session_words,
            "per_session_accuracy": avg_session_accuracy,
            "per_session_minutes": avg_session_minutes,
            "sessions_per_week": sessions_per_week,
            "active_days_in_window": active_days_window,
        },
        "by_date": by_date,
        "by_month": by_month,
        "recent": recent_sessions,
    }


@router.get("/needs-review")
async def get_needs_review(
    limit: int = Query(default=10, ge=1, le=50),
    category_id: Optional[int] = Query(default=None),
    course_id: Optional[int] = Query(default=None),
    lesson_id: Optional[int] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    Word = UserDictionary
    pool_stmt = _apply_scope(
        select(Word).where(Word.student_id == current_user.id),
        category_id=category_id,
        course_id=course_id,
        lesson_id=lesson_id,
    )
    pool = (await db.execute(pool_stmt)).scalars().all()

    def tier(w):
        if (w.review_count or 0) == 0:
            return 0
        if w.review_count > 0:
            acc = (w.correct_count or 0) / w.review_count
            if acc < 0.7:
                return 1
        return 2

    def sort_key(w):
        rc = w.review_count or 0
        acc = (w.correct_count or 0) / rc if rc > 0 else 0.0
        created = w.created_at or datetime(1970, 1, 1)
        return (tier(w), acc, created)

    ranked = sorted(pool, key=sort_key)
    selected = ranked[:limit]

    out = []
    for w in selected:
        rc = w.review_count or 0
        acc = round((w.correct_count or 0) / rc * 100) if rc > 0 else None
        out.append({
            "id": w.id,
            "word": w.word,
            "context": w.context,
            "lesson_id": w.lesson_id,
            "review_count": rc,
            "accuracy": acc,
            "lapses": w.lapses or 0,
            "interval_days": w.interval_days or 0,
            "next_review_at": w.next_review_at.isoformat() if w.next_review_at else None,
        })

    needs_total = sum(
        1 for w in pool
        if (w.review_count or 0) == 0
        or ((w.review_count or 0) > 0 and (w.correct_count or 0) / (w.review_count or 1) < 0.7)
    )
    return {"items": out, "total": needs_total}


@router.get("/breakdown")
async def get_breakdown(
    category_id: Optional[int] = Query(default=None),
    course_id: Optional[int] = Query(default=None),
    lesson_id: Optional[int] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    Word = UserDictionary
    base = _apply_scope(
        select(Word.id, Word.part_of_speech, Course.difficulty_level)
        .outerjoin(Lesson, Lesson.id == Word.lesson_id)
        .outerjoin(Course, Course.id == Lesson.course_id)
        .where(Word.student_id == current_user.id),
        category_id=category_id,
        course_id=course_id,
        lesson_id=lesson_id,
    )
    rows = (await db.execute(base)).all()

    by_difficulty: dict[str, int] = {}
    by_pos: dict[str, int] = {}
    for _wid, pos, diff in rows:
        diff_key = diff or "noma'lum"
        pos_key = (pos or "noma'lum").lower()
        by_difficulty[diff_key] = by_difficulty.get(diff_key, 0) + 1
        by_pos[pos_key] = by_pos.get(pos_key, 0) + 1

    diff_order = ["Beginner", "Intermediate", "Advanced", "Expert"]
    by_difficulty_sorted = {
        **{k: by_difficulty[k] for k in diff_order if k in by_difficulty},
        **{k: v for k, v in by_difficulty.items() if k not in diff_order},
    }
    by_pos_sorted = dict(sorted(by_pos.items(), key=lambda x: -x[1]))

    return {
        "total": len(rows),
        "by_difficulty": by_difficulty_sorted,
        "by_part_of_speech": by_pos_sorted,
    }
