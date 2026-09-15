"""Category-level completion certificates (app/services/category_certificate_service.py
+ the /achievements/category/{id}/download and
/achievements/check-and-earn-certificate-category endpoints).

A category certificate is awarded once a student has actually finished
(100% of active lessons) every published+active course in that category —
mirrors the platform-wide "Full Stack Developer" logic
(_all_published_courses_complete in achievement_service.py), just scoped to
one category instead of every course.

Completion is checked via real lesson completion, NOT via CourseCertificate
existence — see check_category_completion's docstring. That distinction is
exactly what the "false_when_partially_certified"-style tests below guard,
and it's the fix for a real production bug: a student can 100% every
lesson in every course of a category without a CourseCertificate row ever
being minted for one of them (it's a lazy side effect of the achievement
flow, not automatic), which made an actually-finished student see "siz
hali ... tugatmagansiz" when the completion check keyed off certificates.
"""
import uuid

import pytest_asyncio

from app.models.category import Category
from app.models.course import Course
from app.models.lesson import Lesson, LessonCompletion
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


async def _complete_lesson_only(db_session, student_id: int, lesson: Lesson) -> None:
    """Marks the lesson done WITHOUT going through award_certificate() —
    so no CourseCertificate row exists and the category-cert auto-award
    hook never fires. Use this to test completion/award logic against
    real lesson-completion state in isolation from that hook."""
    db_session.add(LessonCompletion(student_id=student_id, lesson_id=lesson.id))
    await db_session.commit()


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


async def test_check_category_completion_true_from_lessons_alone_no_certificates_exist(async_client, db_session, category):
    """Regression test for the production bug: every lesson done, but zero
    CourseCertificate rows exist for either course (award_certificate was
    never called for them — e.g. the student never hit a page that runs
    check_and_award_achievements). Completion must still read True."""
    teacher_id, _ = await _register_and_login(async_client, "teacher")
    student_id, _ = await _register_and_login(async_client, "student")

    course_a, lesson_a = await _make_published_course(db_session, category.id, teacher_id, "Course A")
    course_b, lesson_b = await _make_published_course(db_session, category.id, teacher_id, "Course B")
    await db_session.commit()

    await _complete_lesson_only(db_session, student_id, lesson_a)
    await _complete_lesson_only(db_session, student_id, lesson_b)

    assert await achievement_service.check_category_completion(db_session, student_id, category.id) is True


async def test_award_category_certificate_backfills_missing_course_certificates(async_client, db_session, category):
    """award_category_certificate must also mint the CourseCertificate rows
    that were missing despite genuine completion, so each course's own
    certificate becomes downloadable too — not just the category one."""
    teacher_id, _ = await _register_and_login(async_client, "teacher")
    student_id, _ = await _register_and_login(async_client, "student")

    course_a, lesson_a = await _make_published_course(db_session, category.id, teacher_id, "Course A")
    course_b, lesson_b = await _make_published_course(db_session, category.id, teacher_id, "Course B")
    await db_session.commit()

    await _complete_lesson_only(db_session, student_id, lesson_a)
    await _complete_lesson_only(db_session, student_id, lesson_b)

    assert await achievement_service.get_course_certificate(db_session, student_id, course_a.id) is None
    assert await achievement_service.get_course_certificate(db_session, student_id, course_b.id) is None

    cert = await achievement_service.award_category_certificate(db_session, student_id, category.id)
    assert cert is not None

    assert await achievement_service.get_course_certificate(db_session, student_id, course_a.id) is not None
    assert await achievement_service.get_course_certificate(db_session, student_id, course_b.id) is not None


async def test_award_category_certificate_is_idempotent(async_client, db_session, category):
    teacher_id, _ = await _register_and_login(async_client, "teacher")
    student_id, _ = await _register_and_login(async_client, "student")

    course, lesson = await _make_published_course(db_session, category.id, teacher_id, "Only Course")
    await db_session.commit()
    # Lesson-only completion (not _complete_and_certify) so the auto-award
    # hook in award_certificate() doesn't pre-empt the explicit calls below.
    await _complete_lesson_only(db_session, student_id, lesson)

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

    course, lesson = await _make_published_course(db_session, category.id, teacher_id, "Only Course")
    await db_session.commit()
    # Lesson-only completion so the endpoint call below is the one that
    # actually issues the category certificate (not the award_certificate()
    # hook, and not a pre-existing CourseCertificate row).
    await _complete_lesson_only(db_session, student_id, lesson)

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
