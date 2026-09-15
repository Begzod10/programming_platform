"""Tests for GET /api/v1/integrations/progress — the classroom_v2
server-to-server progress pull (request #47, 2026-09-14), and the
X-Internal-Secret guard added to /bot/search-student and
/bot/student-stats/{id} in the same request (§5's security finding: those
two had no auth at all).
"""
import uuid

import pytest

from app.config import settings
from app.models.user import Student
from app.models.course import Course, student_courses
from app.models.lesson import Lesson, LessonCompletion
from app.models.exercise import Exercise, ExerciseSubmission
from app.models.project import Project
from app.models.achievement import Achievement
from app.models.student_achievement import StudentAchievement

TEST_KEY = "test-classroom-integration-secret"


@pytest.fixture(autouse=True)
def classroom_key(monkeypatch):
    monkeypatch.setattr(settings, "CLASSROOM_INTEGRATION_SECRET", TEST_KEY)
    yield


def _uname(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


async def _make_student(db_session, **overrides) -> Student:
    defaults = dict(
        username=_uname("prog"),
        email=f"{_uname('prog')}@gennis.uz",
        hashed_password="external_auth",
        full_name="Progress Test",
        role="student",
    )
    defaults.update(overrides)
    student = Student(**defaults)
    db_session.add(student)
    await db_session.commit()
    await db_session.refresh(student)
    return student


# ── Auth guard ────────────────────────────────────────────────────────────

async def test_progress_503_when_secret_not_configured(async_client, monkeypatch):
    monkeypatch.setattr(settings, "CLASSROOM_INTEGRATION_SECRET", "")
    resp = await async_client.get(
        "/api/v1/integrations/progress",
        params={"source": "gennis", "ext_id": 1},
        headers={"X-Classroom-Key": "anything"},
    )
    assert resp.status_code == 503


async def test_progress_401_with_wrong_key(async_client):
    resp = await async_client.get(
        "/api/v1/integrations/progress",
        params={"source": "gennis", "ext_id": 1},
        headers={"X-Classroom-Key": "wrong"},
    )
    assert resp.status_code == 401


async def test_progress_401_with_no_key(async_client):
    resp = await async_client.get(
        "/api/v1/integrations/progress", params={"source": "gennis", "ext_id": 1},
    )
    assert resp.status_code == 401


async def test_progress_400_bad_source(async_client):
    resp = await async_client.get(
        "/api/v1/integrations/progress",
        params={"source": "bogus", "ext_id": 1},
        headers={"X-Classroom-Key": TEST_KEY},
    )
    assert resp.status_code == 400


# ── Lookup ────────────────────────────────────────────────────────────────

async def test_progress_not_found_returns_found_false_not_404(async_client):
    resp = await async_client.get(
        "/api/v1/integrations/progress",
        params={"source": "gennis", "ext_id": 999999999},
        headers={"X-Classroom-Key": TEST_KEY},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"found": False, "source": "gennis", "ext_id": 999999999}


async def test_progress_finds_student_by_turon_id(async_client, db_session):
    tid = 555001
    await _make_student(db_session, turon_id=tid)

    resp = await async_client.get(
        "/api/v1/integrations/progress",
        params={"source": "turon", "ext_id": tid},
        headers={"X-Classroom-Key": TEST_KEY},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["found"] is True
    assert body["source"] == "turon"
    assert body["ext_id"] == tid


# ── Full shape, with real course/exercise/project/achievement data ────────

async def test_progress_full_shape_for_an_active_student(async_client, db_session):
    gid = 555002
    student = await _make_student(db_session, gennis_id=gid, total_points=40, lifetime_points=40, global_rank=114, current_streak=1, longest_streak=5)

    course = Course(
        title="HTML asoslari", description="d", instructor_id=student.id,
        difficulty_level="Beginner", duration_weeks=4, max_points=100, display_order=1,
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)

    lesson1 = Lesson(course_id=course.id, title="L1", order=1)
    lesson2 = Lesson(course_id=course.id, title="L2", order=2)
    db_session.add_all([lesson1, lesson2])
    await db_session.commit()
    await db_session.refresh(lesson1)
    await db_session.refresh(lesson2)

    db_session.add(LessonCompletion(student_id=student.id, lesson_id=lesson1.id))
    await db_session.execute(student_courses.insert().values(student_id=student.id, course_id=course.id))

    exercise = Exercise(lesson_id=lesson1.id, title="Ex1", description="d", exercise_type="text_input")
    db_session.add(exercise)
    await db_session.commit()
    await db_session.refresh(exercise)

    db_session.add(ExerciseSubmission(exercise_id=exercise.id, student_id=student.id, student_answer="x", is_correct=True))

    project = Project(
        student_id=student.id, title="My Project", description="d",
        difficulty_level="Beginner", status="Submitted", points_earned=30,
        github_url="https://github.com/x/y",
    )
    db_session.add(project)

    achievement = Achievement(
        name="First Steps", description="d", badge_image_url="", points_reward=10,
        criteria_type="lessons", criteria_value=1,
    )
    db_session.add(achievement)
    await db_session.commit()
    await db_session.refresh(achievement)
    db_session.add(StudentAchievement(student_id=student.id, achievement_id=achievement.id))
    await db_session.commit()

    resp = await async_client.get(
        "/api/v1/integrations/progress",
        params={"source": "gennis", "ext_id": gid},
        headers={"X-Classroom-Key": TEST_KEY},
    )
    assert resp.status_code == 200
    body = resp.json()

    assert body["found"] is True
    assert body["student_id"] == student.id
    assert body["profile"]["total_points"] == 40
    assert body["profile"]["global_rank"] == 114
    assert body["profile"]["current_streak"] == 1

    assert len(body["courses"]) == 1
    c = body["courses"][0]
    assert c["id"] == course.id
    assert c["lessons_total"] == 2
    assert c["lessons_done"] == 1
    assert c["progress_pct"] == 50
    assert c["exercises_total"] == 1
    assert c["exercises_correct"] == 1

    assert body["overall"]["exercises_total"] == 1
    assert body["overall"]["exercises_correct"] == 1
    assert body["overall"]["projects_total"] == 1
    assert body["overall"]["projects_submitted"] == 1

    assert len(body["projects"]) == 1
    assert body["projects"][0]["title"] == "My Project"
    assert body["projects"][0]["github_url"] == "https://github.com/x/y"

    assert len(body["achievements"]) == 1
    assert body["achievements"][0]["title"] == "First Steps"


# ── bot_stats.py's newly-added guard ────────────────────────────────────────

@pytest.fixture(autouse=True)
def bot_secret(monkeypatch):
    monkeypatch.setattr(settings, "PARENT_BOT_SECRET", TEST_KEY)
    yield


async def test_search_student_503_when_bot_secret_not_configured(async_client, monkeypatch):
    monkeypatch.setattr(settings, "PARENT_BOT_SECRET", "")
    resp = await async_client.get("/api/v1/bot/search-student", params={"q": "ab"})
    assert resp.status_code == 503


async def test_search_student_401_without_secret(async_client):
    resp = await async_client.get("/api/v1/bot/search-student", params={"q": "ab"})
    assert resp.status_code == 401


async def test_search_student_200_with_correct_secret(async_client, db_session):
    await _make_student(db_session, full_name="Findable Student")
    resp = await async_client.get(
        "/api/v1/bot/search-student",
        params={"q": "Findable"},
        headers={"X-Internal-Secret": TEST_KEY},
    )
    assert resp.status_code == 200
    assert any(s["name"] == "Findable Student" for s in resp.json())


async def test_student_stats_401_without_secret(async_client, db_session):
    student = await _make_student(db_session)
    resp = await async_client.get(f"/api/v1/bot/student-stats/{student.id}")
    assert resp.status_code == 401


async def test_student_stats_200_with_correct_secret(async_client, db_session):
    student = await _make_student(db_session)
    resp = await async_client.get(
        f"/api/v1/bot/student-stats/{student.id}",
        headers={"X-Internal-Secret": TEST_KEY},
    )
    assert resp.status_code == 200
    assert resp.json()["student_id"] == student.id
