"""Category-level completion certificates (app/services/category_certificate_service.py
+ the /achievements/category/{id}/download and
/achievements/check-and-earn-certificate-category endpoints).

A category certificate is awarded once a student holds a CourseCertificate
for every published+active course (with >=1 active lesson) in that
category — mirrors the platform-wide "Full Stack Developer" logic
(_all_published_courses_complete in achievement_service.py), just scoped to
one category instead of every course.
"""
import uuid

import pytest_asyncio

from app.models.category import Category
from app.models.course import Course
from app.models.lesson import Lesson, LessonCompletion
from app.models.student_achievement import CourseCertificate
from app.services import achievement_service


async def _register_and_login(async_client, prefix: str):
    uid = uuid.uuid4().hex[:8]
    username, password = f"{prefix}_{uid}", "securepass123"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{prefix}_{uid}@example.com", "password": password},
    )
    assert reg.status_code == 201, f"Register failed: {reg.text}"
    student_id = reg.json()["user"]["id"]

    login = await async_client.post(
        "/api/v1/auth/login", json={"username": username, "password": password},
    )
    assert login.status_code == 200, f"Login failed: {login.text}"
    token = login.json()["access_token"]
    return student_id, {"Authorization": f"Bearer {token}"}


async def _make_published_course(db_session, category_id: int, instructor_id: int, title: str) -> tuple[Course, Lesson]:
    course = Course(
        title=title, description="test course", instructor_id=instructor_id,
        difficulty_level="Beginner", duration_weeks=1, max_points=100,
        category_id=category_id, is_active=True, is_published=True,
    )
    db_session.add(course)
    await db_session.flush()
    lesson = Lesson(course_id=course.id, title="L1", is_active=True)
    db_session.add(lesson)
    await db_session.flush()
    return course, lesson


async def _complete_and_certify(db_session, student_id: int, course: Course, lesson: Lesson) -> None:
    """Completes the lesson and goes through the real award_certificate()
    service call — this is what fires the category-certificate auto-award
    hook (step 6 in award_certificate). Use this when that side effect is
    exactly what's being tested."""
    db_session.add(LessonCompletion(student_id=student_id, lesson_id=lesson.id))
    await db_session.flush()
    await db_session.commit()
    cert = await achievement_service.award_certificate(db_session, student_id, course.id)
    assert cert is not None, "award_certificate should have issued a CourseCertificate"


async def _certify_course_directly(db_session, student_id: int, course_id: int) -> None:
    """Inserts a CourseCertificate row without going through
    award_certificate() — so the category-certificate auto-award hook never
    fires. Use this when a test wants to control category-cert timing
    itself (e.g. testing award_category_certificate's own idempotency)."""
    db_session.add(CourseCertificate(student_id=student_id, course_id=course_id))
    await db_session.commit()


@pytest_asyncio.fixture
async def category(db_session) -> Category:
    cat = Category(name=f"Test Category {uuid.uuid4().hex[:6]}", slug=f"test-cat-{uuid.uuid4().hex[:6]}")
    db_session.add(cat)
    await db_session.flush()
    await db_session.commit()
    return cat


async def test_check_category_completion_false_with_no_courses(db_session, category):
    assert await achievement_service.check_category_completion(db_session, student_id=1, category_id=category.id) is False


async def test_check_category_completion_false_when_partially_certified(async_client, db_session, category):
    teacher_id, _ = await _register_and_login(async_client, "teacher")
    student_id, _ = await _register_and_login(async_client, "student")

    course_a, lesson_a = await _make_published_course(db_session, category.id, teacher_id, "Course A")
    course_b, lesson_b = await _make_published_course(db_session, category.id, teacher_id, "Course B")
    await db_session.commit()

    await _complete_and_certify(db_session, student_id, course_a, lesson_a)
    # Course B intentionally left uncompleted.

    assert await achievement_service.check_category_completion(db_session, student_id, category.id) is False


async def test_check_category_completion_true_when_fully_certified(async_client, db_session, category):
    teacher_id, _ = await _register_and_login(async_client, "teacher")
    student_id, _ = await _register_and_login(async_client, "student")

    course_a, lesson_a = await _make_published_course(db_session, category.id, teacher_id, "Course A")
    course_b, lesson_b = await _make_published_course(db_session, category.id, teacher_id, "Course B")
    await db_session.commit()

    await _complete_and_certify(db_session, student_id, course_a, lesson_a)
    await _complete_and_certify(db_session, student_id, course_b, lesson_b)

    assert await achievement_service.check_category_completion(db_session, student_id, category.id) is True


async def test_award_category_certificate_is_idempotent(async_client, db_session, category):
    teacher_id, _ = await _register_and_login(async_client, "teacher")
    student_id, _ = await _register_and_login(async_client, "student")

    course, _lesson = await _make_published_course(db_session, category.id, teacher_id, "Only Course")
    await db_session.commit()
    # Direct insert (not _complete_and_certify) so the auto-award hook in
    # award_certificate() doesn't pre-empt the explicit calls below.
    await _certify_course_directly(db_session, student_id, course.id)

    first = await achievement_service.award_category_certificate(db_session, student_id, category.id)
    assert first is not None

    second = await achievement_service.award_category_certificate(db_session, student_id, category.id)
    assert second is None, "awarding twice must not create a duplicate row"


async def test_award_certificate_auto_awards_category_certificate_on_last_course(async_client, db_session, category):
    """Integration check for the hook added to award_certificate(): finishing
    the LAST course of a category must mint the category certificate right
    away, without a separate explicit call."""
    teacher_id, _ = await _register_and_login(async_client, "teacher")
    student_id, _ = await _register_and_login(async_client, "student")

    course_a, lesson_a = await _make_published_course(db_session, category.id, teacher_id, "Course A")
    course_b, lesson_b = await _make_published_course(db_session, category.id, teacher_id, "Course B")
    await db_session.commit()

    await _complete_and_certify(db_session, student_id, course_a, lesson_a)
    assert await achievement_service.get_category_certificate(db_session, student_id, category.id) is None

    await _complete_and_certify(db_session, student_id, course_b, lesson_b)
    assert await achievement_service.get_category_certificate(db_session, student_id, category.id) is not None


async def test_download_category_certificate_400_before_completion(async_client, db_session, category):
    teacher_id, _ = await _register_and_login(async_client, "teacher")
    student_id, student_headers = await _register_and_login(async_client, "student")

    course_a, lesson_a = await _make_published_course(db_session, category.id, teacher_id, "Course A")
    await db_session.commit()

    resp = await async_client.get(f"/api/v1/achievements/category/{category.id}/download", headers=student_headers)
    assert resp.status_code == 400


async def test_check_and_earn_then_download_category_certificate(async_client, db_session, category):
    teacher_id, _ = await _register_and_login(async_client, "teacher")
    student_id, student_headers = await _register_and_login(async_client, "student")

    course, _lesson = await _make_published_course(db_session, category.id, teacher_id, "Only Course")
    await db_session.commit()
    # Direct insert so the endpoint call below is the one that actually
    # issues the category certificate (not the award_certificate() hook).
    await _certify_course_directly(db_session, student_id, course.id)

    check_resp = await async_client.post(
        f"/api/v1/achievements/check-and-earn-certificate-category?category_id={category.id}",
        headers=student_headers,
    )
    assert check_resp.status_code == 200
    assert check_resp.json()["issued"] is True

    dl_resp = await async_client.get(f"/api/v1/achievements/category/{category.id}/download", headers=student_headers)
    assert dl_resp.status_code == 200
    assert dl_resp.headers["content-type"] == "application/pdf"


async def test_check_and_earn_reports_already_issued_when_hook_got_there_first(async_client, db_session, category):
    """The award_certificate() hook (step 6) already mints the category
    certificate the moment the last course is completed — a subsequent
    check-and-earn call must report "already issued", not fail, and the
    certificate must still be downloadable."""
    teacher_id, _ = await _register_and_login(async_client, "teacher")
    student_id, student_headers = await _register_and_login(async_client, "student")

    course, lesson = await _make_published_course(db_session, category.id, teacher_id, "Only Course")
    await db_session.commit()
    await _complete_and_certify(db_session, student_id, course, lesson)

    check_resp = await async_client.post(
        f"/api/v1/achievements/check-and-earn-certificate-category?category_id={category.id}",
        headers=student_headers,
    )
    assert check_resp.status_code == 200
    assert check_resp.json()["issued"] is False

    dl_resp = await async_client.get(f"/api/v1/achievements/category/{category.id}/download", headers=student_headers)
    assert dl_resp.status_code == 200
