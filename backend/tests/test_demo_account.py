"""Demo accounts: sign-up by name only, a hard allow-list, no points, invisible to stats."""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.core.demo import DEMO_COURSE_ID, DEMO_LESSON_IDS, demo_allows
from app.db.database import AsyncSessionLocal
from app.models.user import Student

L = sorted(DEMO_LESSON_IDS)
C = DEMO_COURSE_ID


# ── the allow-list (pure) ────────────────────────────────────────────────────

@pytest.mark.parametrize("method,path", [
    ("GET", "/api/v1/auth/me"),
    ("GET", "/api/v1/student/me"),
    ("GET", "/api/v1/courses/"),
    ("GET", f"/api/v1/courses/{C}"),
    ("GET", f"/api/v1/courses/{C}/lessons"),
    ("GET", f"/api/v1/courses/{C}/lessons/{L[0]}"),
    ("GET", f"/api/v1/courses/{C}/lessons/{L[1]}/exercises"),
    ("POST", f"/api/v1/courses/{C}/lessons/{L[1]}/exercises/7/submit"),
    ("POST", f"/api/v1/lessons/{L[1]}/complete"),
    ("GET", f"/api/v1/lessons/{L[0]}/is-completed"),
])
def test_demo_may_use_the_two_lessons(method, path):
    assert demo_allows(method, path)


@pytest.mark.parametrize("method,path", [
    ("POST", f"/api/v1/courses/{C}/lessons/{L[1]}/submit"),          # lesson project
    ("POST", "/api/v1/project/"),
    ("POST", "/api/v1/project/5/upload-zip"),
    ("POST", "/api/v1/project/5/submit"),
    ("GET", f"/api/v1/courses/{C}/lessons/{max(L) + 1000}"),         # a later lesson
    ("GET", f"/api/v1/courses/{C + 1}/lessons"),                     # another course
    ("POST", f"/api/v1/lessons/{max(L) + 1000}/complete"),
    ("POST", f"/api/v1/courses/{C}/enroll"),
    ("PUT", "/api/v1/auth/me"),
    ("DELETE", "/api/v1/auth/me"),
    ("GET", "/api/v1/rankings/leaderboard"),
    ("GET", "/api/v1/dictionary/"),
    ("POST", f"/api/v1/lessons/{L[0]}/feedback"),
    ("GET", "/api/v1/store/items"),
    ("GET", "/api/v1/teacher/statistics/overview"),
])
def test_demo_is_refused_everything_else(method, path):
    assert not demo_allows(method, path)


# ── endpoint ─────────────────────────────────────────────────────────────────

async def _demo(async_client, first="Ali", last="Valiyev"):
    r = await async_client.post("/api/v1/auth/demo", json={"first_name": first, "last_name": last})
    assert r.status_code == 201, r.text
    return r.json()


async def test_demo_signup_needs_only_a_name(async_client):
    body = await _demo(async_client)
    user = body["user"]
    assert user["is_demo"] is True and user["role"] == "student"
    assert user["full_name"] == "Ali Valiyev"
    assert user["username"].startswith("demo_")
    assert body["access_token"]


@pytest.mark.parametrize("first,last", [
    ("A", "Valiyev"), ("Ali", ""), ("Ali1", "Valiyev"), ("<script>", "Valiyev"),
    ("http://x.co", "Valiyev"), ("x" * 41, "Valiyev"),
])
async def test_demo_signup_rejects_bad_names(async_client, first, last):
    r = await async_client.post("/api/v1/auth/demo", json={"first_name": first, "last_name": last})
    assert r.status_code == 422


async def test_demo_accepts_uzbek_and_russian_names(async_client):
    assert (await _demo(async_client, "Oʻtkir", "G'ulomov"))["user"]["is_demo"]
    assert (await _demo(async_client, "Анна", "Иванова"))["user"]["is_demo"]


async def test_demo_cannot_log_in_with_a_password(async_client):
    user = (await _demo(async_client))["user"]
    r = await async_client.post("/api/v1/auth/login", json={"username": user["username"], "password": "anything-at-all"})
    assert r.status_code in (400, 401, 403)


async def test_demo_token_works_for_me_but_not_for_other_areas(async_client):
    h = {"Authorization": f"Bearer {(await _demo(async_client))['access_token']}"}
    assert (await async_client.get("/api/v1/auth/me", headers=h)).status_code == 200
    for method, path in [("get", "/api/v1/rankings/leaderboard"),
                         ("get", "/api/v1/dictionary/"),
                         ("post", "/api/v1/project/")]:
        r = await getattr(async_client, method)(path, headers=h)
        assert r.status_code == 403, (path, r.status_code)
        assert "Demo" in r.json()["error"]["message"]


async def test_demo_cannot_submit_a_project(async_client):
    h = {"Authorization": f"Bearer {(await _demo(async_client))['access_token']}"}
    r = await async_client.post(f"/api/v1/courses/{C}/lessons/{L[1]}/submit", headers=h, json={})
    assert r.status_code == 403
    r = await async_client.post("/api/v1/project/1/upload-zip", headers=h)
    assert r.status_code == 403


# ── invisible to stats, earns nothing ────────────────────────────────────────

async def test_demo_earns_no_points_and_has_no_ranking(async_client):
    from app.services.ranking_service import RankingService
    from app.models.ranking import Ranking
    user = (await _demo(async_client))["user"]
    async with AsyncSessionLocal() as db:
        await RankingService(db).add_points_to_student(user["id"], 50)
        s = (await db.execute(select(Student).where(Student.id == user["id"]))).scalar_one()
        assert s.total_points == 0 and s.lifetime_points == 0
        assert (await db.execute(select(Ranking).where(Ranking.student_id == user["id"]))).first() is None
        assert await RankingService(db).create_ranking(user["id"]) is None


async def test_demo_is_not_in_the_leaderboard(async_client):
    from app.services.ranking_service import RankingService
    user = (await _demo(async_client, "Zafar", "Demoyev"))["user"]
    async with AsyncSessionLocal() as db:
        board = await RankingService(db).get_leaderboard(limit=500)
    flat = repr(board)
    assert "Zafar Demoyev" not in flat and user["username"] not in flat


# ── the real lesson flow on the demo course ──────────────────────────────────

async def _seed_demo_course():
    """Course 9 with lessons 4, 5 (demo) and 6 (locked), created with those ids.

    The test DB is shared by the whole run, so another test may already have a
    course 9 or lessons 4/5/6 (under some other course): take them over."""
    from app.models.course import Course
    from app.models.lesson import Lesson
    from app.models.user import UserRole
    async with AsyncSessionLocal() as db:
        course = (await db.execute(select(Course).where(Course.id == DEMO_COURSE_ID))).scalar_one_or_none()
        if course is None:
            teacher = Student(username=f"t_{uuid.uuid4().hex[:6]}", email=f"t_{uuid.uuid4().hex[:6]}@x.uz",
                              hashed_password="x", role=UserRole.teacher, full_name="T")
            db.add(teacher)
            await db.flush()
            db.add(Course(id=DEMO_COURSE_ID, title="HTML CSS", description="d", instructor_id=teacher.id,
                          difficulty_level="Beginner", duration_weeks=4, max_points=100,
                          is_active=True, is_published=True))
            await db.flush()
        else:
            course.is_active = course.is_published = True
        for i, lid in enumerate(sorted(DEMO_LESSON_IDS) + [max(DEMO_LESSON_IDS) + 1]):
            lesson = (await db.execute(select(Lesson).where(Lesson.id == lid))).scalar_one_or_none()
            if lesson is None:
                db.add(Lesson(id=lid, course_id=DEMO_COURSE_ID, title=f"Dars {i + 1}", order=i,
                              points_reward=10, is_active=True, is_published=True))
            else:
                lesson.course_id = DEMO_COURSE_ID
                lesson.is_active = lesson.is_published = True
        await db.commit()


async def test_demo_sees_only_its_two_lessons_and_earns_nothing(async_client):
    await _seed_demo_course()
    body = await _demo(async_client, "Dars", "Ko'ruvchi")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    uid = body["user"]["id"]

    lessons = await async_client.get(f"/api/v1/courses/{C}/lessons", headers=h)
    assert lessons.status_code == 200, lessons.text
    assert {l["id"] for l in lessons.json()} == set(DEMO_LESSON_IDS)

    locked = max(DEMO_LESSON_IDS) + 1
    assert (await async_client.get(f"/api/v1/courses/{C}/lessons/{locked}", headers=h)).status_code == 403
    assert (await async_client.post(f"/api/v1/lessons/{locked}/complete", headers=h)).status_code == 403

    first = min(DEMO_LESSON_IDS)
    done = await async_client.post(f"/api/v1/lessons/{first}/complete", headers=h)
    assert done.status_code == 200, done.text

    async with AsyncSessionLocal() as db:
        s = (await db.execute(select(Student).where(Student.id == uid))).scalar_one()
        assert s.total_points == 0 and s.lifetime_points == 0


async def test_demo_is_not_listed_among_the_courses_students(async_client):
    from app.models.course import student_courses
    await _seed_demo_course()
    uid = (await _demo(async_client, "Royxat", "Tashqarisi"))["user"]["id"]
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(select(student_courses).where(student_courses.c.student_id == uid))).all()
    assert rows == []


# ── purge ────────────────────────────────────────────────────────────────────

async def test_expired_demo_accounts_are_purged_and_fresh_ones_kept(async_client):
    from app import scheduler
    old = (await _demo(async_client, "Eski", "Demo"))["user"]["id"]
    fresh = (await _demo(async_client, "Yangi", "Demo"))["user"]["id"]
    async with AsyncSessionLocal() as db:
        s = (await db.execute(select(Student).where(Student.id == old))).scalar_one()
        s.created_at = datetime.now(timezone.utc) - timedelta(days=30)
        await db.commit()
    await scheduler.job_purge_expired_demo_accounts()
    async with AsyncSessionLocal() as db:
        assert (await db.execute(select(Student).where(Student.id == old))).first() is None
        assert (await db.execute(select(Student).where(Student.id == fresh))).first() is not None
