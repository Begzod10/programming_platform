"""The parent/group bot reads weekly_lessons, weekly_exercises and weekly_rank from /bot/student-stats; they must exist
and cover the current calendar week (Monday 00:00 Asia/Tashkent), with weekly points including today's."""
import uuid
from datetime import timedelta

import pytest_asyncio
from sqlalchemy import delete, select

from app.config import settings
from app.db.database import AsyncSessionLocal
from app.models.course import Course, student_courses
from app.models.exercise import Exercise, ExerciseSubmission
from app.models.lesson import Lesson, LessonCompletion
from app.models.ranking import Ranking
from app.models.user import Student
from app.utils.datetime_utils import utcnow

H = {"X-Internal-Secret": "test-secret-xyz"}
_made: list = []   # (student_id, course_id) pairs; other suites assume low, fixed course/lesson ids, so clean up


@pytest_asyncio.fixture(autouse=True)
async def _cleanup():
    yield
    async with AsyncSessionLocal() as db:
        for sid, cid in _made:
            lesson_ids = (await db.execute(select(Lesson.id).where(Lesson.course_id == cid))).scalars().all()
            ex_ids = (await db.execute(select(Exercise.id).where(Exercise.lesson_id.in_(lesson_ids)))).scalars().all()
            await db.execute(delete(ExerciseSubmission).where(ExerciseSubmission.exercise_id.in_(ex_ids)))
            await db.execute(delete(Exercise).where(Exercise.id.in_(ex_ids)))
            await db.execute(delete(LessonCompletion).where(LessonCompletion.lesson_id.in_(lesson_ids)))
            await db.execute(delete(Lesson).where(Lesson.id.in_(lesson_ids)))
            await db.execute(delete(student_courses).where(student_courses.c.course_id == cid))
            await db.execute(delete(Course).where(Course.id == cid))
            await db.execute(delete(Ranking).where(Ranking.student_id == sid))
            await db.execute(delete(Student).where(Student.id == sid))
        await db.commit()
    _made.clear()


async def _setup(*, lessons=3):
    uid = uuid.uuid4().hex[:8]
    async with AsyncSessionLocal() as db:
        s = Student(username=f"ws_{uid}", email=f"ws_{uid}@example.com", hashed_password="x", full_name="W Student")
        db.add(s)
        await db.flush()
        c = Course(title="Kurs", description="d", instructor_id=s.id, difficulty_level="Beginner",
                   duration_weeks=1, max_points=10, is_published=True)
        db.add(c)
        await db.flush()
        await db.execute(student_courses.insert().values(student_id=s.id, course_id=c.id))
        ls = []
        for i in range(lessons):
            l = Lesson(course_id=c.id, title=f"L{i}", order=i)
            db.add(l)
            ls.append(l)
        await db.flush()
        ex = Exercise(lesson_id=ls[0].id, title="e", description="d", exercise_type="text_input")
        db.add(ex)
        await db.flush()
        await db.commit()
        _made.append((s.id, c.id))
        return s.id, [l.id for l in ls], ex.id


async def _complete(sid, lesson_id, when):
    async with AsyncSessionLocal() as db:
        db.add(LessonCompletion(student_id=sid, lesson_id=lesson_id, completed_at=when))
        await db.commit()


async def _submit(sid, ex_id, correct, when):
    async with AsyncSessionLocal() as db:
        db.add(ExerciseSubmission(exercise_id=ex_id, student_id=sid, student_answer="x",
                                  is_correct=correct, submitted_at=when))
        await db.commit()


async def _stats(async_client, monkeypatch, sid):
    monkeypatch.setattr(settings, "PARENT_BOT_SECRET", "test-secret-xyz")
    r = await async_client.get(f"/api/v1/bot/student-stats/{sid}", headers=H)
    assert r.status_code == 200, r.text
    return r.json()


async def test_this_weeks_lessons_and_exercises_are_counted_and_older_ones_are_not(async_client, monkeypatch):
    sid, lessons, ex = await _setup()
    now = utcnow()
    await _complete(sid, lessons[0], now)
    await _complete(sid, lessons[1], now - timedelta(days=30))
    await _submit(sid, ex, True, now)
    await _submit(sid, ex, False, now)
    await _submit(sid, ex, True, now - timedelta(days=30))
    body = await _stats(async_client, monkeypatch, sid)
    assert body["weekly_lessons"] == 1
    assert body["weekly_exercises"] == {"correct": 1, "total": 2}
    c = body["courses"][0]
    assert c["lessons_completed"] == 2 and c["lessons_total"] == 3        # the course totals still count everything


async def test_weekly_points_include_today_and_the_weekly_rank_is_returned(async_client, monkeypatch):
    sid, _, _ = await _setup()
    async with AsyncSessionLocal() as db:
        r = (await db.execute(select(Ranking).where(Ranking.student_id == sid))).scalar_one_or_none()
        if r is None:
            r = Ranking(student_id=sid)
            db.add(r)
        r.weekly_points, r.daily_points, r.weekly_rank = 100, 30, 4
        await db.commit()
    body = await _stats(async_client, monkeypatch, sid)
    assert body["weekly_points"] == 130 and body["weekly_rank"] == 4


async def test_a_student_with_no_activity_gets_zeros(async_client, monkeypatch):
    sid, _, _ = await _setup()
    body = await _stats(async_client, monkeypatch, sid)
    assert body["weekly_lessons"] == 0 and body["weekly_exercises"] == {"correct": 0, "total": 0}
    assert body["weekly_rank"] == 0


def test_the_week_starts_on_monday_midnight_tashkent():
    from datetime import datetime, timezone
    from app.api.v1.endpoints.bot_stats import _week_start_utc
    # Sat 2026-11-07 12:00 UTC -> Monday 2026-11-02 00:00 Tashkent (UTC+5) = Sunday 2026-11-01 19:00 UTC
    assert _week_start_utc(datetime(2026, 11, 7, 12, tzinfo=timezone.utc)) == datetime(2026, 11, 1, 19, tzinfo=timezone.utc)
    # Mon 2026-11-02 00:30 Tashkent (= Sun 19:30 UTC) is already the new week
    assert _week_start_utc(datetime(2026, 11, 1, 19, 30, tzinfo=timezone.utc)) == datetime(2026, 11, 1, 19, tzinfo=timezone.utc)
    # Sun 2026-11-01 23:00 Tashkent (= 18:00 UTC) still belongs to the previous week
    assert _week_start_utc(datetime(2026, 11, 1, 18, tzinfo=timezone.utc)) == datetime(2026, 10, 25, 19, tzinfo=timezone.utc)
