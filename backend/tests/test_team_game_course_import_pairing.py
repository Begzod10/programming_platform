"""
Regression tests for the course-wide UZ/RU pairing bug in
POST /{session_id}/import-questions (course_id path).

Bug: LessonQuestion.order_index only restarts at 0 *within* each lesson —
it is not globally unique across a course. The course-wide import used to
pool every lesson's quiz rows into one flat list ordered by
(lesson_id, order_index), then split that single pool into uz_qs/ru_qs and
zip them together *by position*. Since most lessons in production are
UZ-only (no RU sibling), a UZ question from lesson A would land at the same
position as an unrelated RU question from lesson B and get paired with it —
producing a bilingual GameQuestion whose two language variants were not
translations of each other at all (confirmed in production: GameQuestion id
79, session 33, paired a UZ HTML-extension question with an unrelated RU
HTML-root-tag question).

Fix: group quiz rows by lesson_id first, then pair UZ/RU by position
independently within each lesson's own rows.

Covers:
- Course-wide import: a UZ-only lesson's question must NOT be paired with
  an unrelated RU question from a different lesson.
- Course-wide import: a lesson with a genuinely paired UZ+RU pair must still
  produce a correctly paired bilingual GameQuestion.
- Single-lesson import path (lesson_id given) still pairs correctly —
  regression guard that the course-path fix didn't disturb it.
"""

import uuid

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import update

from app.models.course import Course
from app.models.lesson import Lesson
from app.models.lesson_question import LessonQuestion
from app.models.user import Student, UserRole

BASE = "/api/v1/game-sessions"


@pytest_asyncio.fixture
async def teacher(async_client: AsyncClient, db_session) -> tuple:
    """Register a fresh teacher, return (id, headers)."""
    uid = uuid.uuid4().hex[:8]
    username = f"teacher_{uid}"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "teacherpass123"},
    )
    assert reg.status_code == 201, reg.text
    teacher_id = reg.json()["user"]["id"]

    await db_session.execute(update(Student).where(Student.id == teacher_id).values(role=UserRole.teacher))
    await db_session.commit()

    login = await async_client.post(
        "/api/v1/auth/login", json={"username": username, "password": "teacherpass123"}
    )
    assert login.status_code == 200, login.text
    return teacher_id, {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest_asyncio.fixture
async def course_id(db_session, teacher) -> int:
    teacher_id, _ = teacher
    course = Course(
        title="Test Course", description="Test", instructor_id=teacher_id,
        difficulty_level="Beginner", duration_weeks=1, max_points=100,
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)
    return course.id


@pytest_asyncio.fixture
async def session_id(async_client: AsyncClient, teacher) -> int:
    _, headers = teacher
    resp = await async_client.post(
        BASE,
        json={"title": "Import Pairing Test", "game_type": "individual", "team_count": 2},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def test_course_import_does_not_cross_pair_uz_and_ru_across_lessons(
    async_client: AsyncClient, db_session, teacher, course_id, session_id
):
    """Two lessons in the same course, both with a question at order_index=0:
    - Lesson A: UZ-only quiz question (no RU sibling in the bank at all).
    - Lesson B: a genuinely paired UZ+RU quiz question at order_index=0.

    Before the fix, the flat cross-lesson pool zipped uz_qs[0] (lesson A's
    UZ-only question) with ru_qs[0] (lesson B's RU question) purely because
    both had order_index=0 — producing a GameQuestion whose "translation"
    was actually a different, unrelated question from another lesson.

    After the fix, lesson A's question must import with no RU pairing at
    all (question_text_ru is None), and lesson B's question must be paired
    with its own genuine RU translation.
    """
    _, headers = teacher

    lesson_a = Lesson(course_id=course_id, title="Lesson A: HTML basics", order=0)
    lesson_b = Lesson(course_id=course_id, title="Lesson B: HTML structure", order=1)
    db_session.add_all([lesson_a, lesson_b])
    await db_session.flush()

    # Lesson A: UZ-only — no RU sibling anywhere in the bank for this lesson.
    db_session.add(LessonQuestion(
        lesson_id=lesson_a.id,
        question_text="HTML faylining to'g'ri kengaytmasi qaysi?",
        options=[".html", ".htm2", ".hml", ".htlm"], correct_option=0,
        time_limit=30, points=1000, order_index=0,
    ))

    # Lesson B: a genuinely paired UZ + RU question, also at order_index=0.
    db_session.add(LessonQuestion(
        lesson_id=lesson_b.id,
        question_text="HTML hujjatining ildiz tegi qaysi?",
        options=["<html>", "<body>", "<head>", "<root>"], correct_option=0,
        time_limit=30, points=1000, order_index=0,
    ))
    db_session.add(LessonQuestion(
        lesson_id=lesson_b.id,
        question_text="Какой тег является корневым элементом HTML-документа?",
        options=["<html>", "<body>", "<head>", "<root>"], correct_option=0,
        time_limit=30, points=1000, order_index=0,
    ))
    await db_session.commit()

    resp = await async_client.post(
        f"{BASE}/{session_id}/import-questions",
        params={"course_id": course_id},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 2

    lesson_a_gq = next(q for q in data if "kengaytmasi" in q["question_text"])
    lesson_b_gq = next(q for q in data if "ildiz tegi" in q["question_text"])

    # Lesson A's UZ-only question must NOT have been cross-paired with
    # lesson B's RU question — it has no RU sibling of its own, so
    # question_text_ru must be None.
    assert lesson_a_gq["question_text_ru"] is None, (
        f"Lesson A's UZ-only question got cross-paired with an unrelated "
        f"RU question from another lesson: {lesson_a_gq['question_text_ru']!r}"
    )

    # Lesson B's UZ question must be paired with its own genuine RU
    # translation, not lost or paired with something else.
    assert lesson_b_gq["question_text_ru"] == "Какой тег является корневым элементом HTML-документа?"


async def test_single_lesson_import_still_pairs_uz_ru_correctly(
    async_client: AsyncClient, db_session, teacher, course_id, session_id
):
    """Regression guard: the single-lesson (lesson_id given) import path
    must remain unaffected by the course-path grouping fix — a UZ+RU pair
    within one lesson still imports as one correctly paired GameQuestion."""
    _, headers = teacher

    lesson = Lesson(course_id=course_id, title="Lesson: CSS basics", order=0)
    db_session.add(lesson)
    await db_session.flush()

    db_session.add(LessonQuestion(
        lesson_id=lesson.id,
        question_text="CSS nima uchun ishlatiladi?",
        options=["Stil berish", "Server", "Ma'lumotlar bazasi", "Tarmoq"], correct_option=0,
        time_limit=30, points=1000, order_index=0,
    ))
    db_session.add(LessonQuestion(
        lesson_id=lesson.id,
        question_text="Для чего используется CSS?",
        options=["Стилизация", "Сервер", "База данных", "Сеть"], correct_option=0,
        time_limit=30, points=1000, order_index=0,
    ))
    await db_session.commit()

    resp = await async_client.post(
        f"{BASE}/{session_id}/import-questions",
        params={"lesson_id": lesson.id},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 1
    q = data[0]
    assert q["question_text"] == "CSS nima uchun ishlatiladi?"
    assert q["question_text_ru"] == "Для чего используется CSS?"
    assert q["options"][q["correct_option"]] == "Stil berish"
    assert q["options_ru"][q["correct_option"]] == "Стилизация"
