"""
Integration tests for importing bug-hunt questions from the LessonQuestion
bank into a game session via POST /{session_id}/import-questions.

Covers:
- Bug-hunt rows import correctly (server-derived shuffle, same guarantees as
  the single-question add_bug_question endpoint)
- Mixed quiz + bug_hunt rows on the same lesson both import in one call
- The pre-existing quiz-only import path is unchanged by the refactor that
  split it from the new bug_hunt branch
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
async def lesson_id(db_session, teacher) -> int:
    teacher_id, _ = teacher
    course = Course(
        title="Test Course", description="Test", instructor_id=teacher_id,
        difficulty_level="Beginner", duration_weeks=1, max_points=100,
    )
    db_session.add(course)
    await db_session.flush()

    lesson = Lesson(course_id=course.id, title="Test Lesson", points_reward=50)
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(lesson)
    return lesson.id


@pytest_asyncio.fixture
async def session_id(async_client: AsyncClient, teacher) -> int:
    _, headers = teacher
    resp = await async_client.post(
        BASE,
        json={"title": "Import Test", "game_type": "individual", "team_count": 2},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def test_import_bug_hunt_question_from_lesson(
    async_client: AsyncClient, db_session, teacher, lesson_id, session_id
):
    _, headers = teacher
    db_session.add(LessonQuestion(
        lesson_id=lesson_id,
        question_text="Nega natija noto'g'ri?",
        question_text_ru="Почему результат неверный?",
        time_limit=90, points=1500, order_index=0,
        question_kind="bug_hunt",
        code_snippet="function sum(a, b) {\n  return a - b;\n}\nconsole.log(sum(2, 3));",
        code_language="javascript",
        bug_line=2,
        distractor_lines=[1, 4],
        bug_explanation="a - b o'rniga a + b bo'lishi kerak",
    ))
    await db_session.commit()

    resp = await async_client.post(
        f"{BASE}/{session_id}/import-questions",
        params={"lesson_id": lesson_id},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 1
    q = data[0]
    assert q["question_kind"] == "bug_hunt"
    assert q["code_language"] == "javascript"
    assert q["bug_line"] == 2
    assert set(q["options"]) == {"2", "1", "4"}
    assert q["options"][q["correct_option"]] == "2"
    # question_text_ru must survive the import, same as bug_explanation_ru —
    # this was the gap: the bank column existed for years with nothing ever
    # copying it into the live GameQuestion.
    assert q["question_text_ru"] == "Почему результат неверный?"


async def test_import_mixed_quiz_and_bug_hunt_from_lesson(
    async_client: AsyncClient, db_session, teacher, lesson_id, session_id
):
    _, headers = teacher
    db_session.add(LessonQuestion(
        lesson_id=lesson_id, question_text="Python nima?",
        options=["Til", "Ilon", "Kitob", "Fayl"], correct_option=0,
        time_limit=30, points=1000, order_index=0,
    ))
    db_session.add(LessonQuestion(
        lesson_id=lesson_id, question_text="Xato qayerda?",
        time_limit=90, points=1500, order_index=1,
        question_kind="bug_hunt",
        code_snippet="a = 1\nb = 2\nprint(a - b)",
        code_language="python",
        bug_line=3,
        distractor_lines=[1, 2],
        bug_explanation="+ bo'lishi kerak edi",
    ))
    await db_session.commit()

    resp = await async_client.post(
        f"{BASE}/{session_id}/import-questions",
        params={"lesson_id": lesson_id},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 2
    kinds = {q["question_kind"] for q in data}
    assert kinds == {"quiz", "bug_hunt"}

    quiz_q = next(q for q in data if q["question_kind"] == "quiz")
    assert quiz_q["options"][quiz_q["correct_option"]] == "Til"

    bug_q = next(q for q in data if q["question_kind"] == "bug_hunt")
    assert bug_q["options"][bug_q["correct_option"]] == "3"


async def test_import_question_kind_filter_selects_only_that_kind(
    async_client: AsyncClient, db_session, teacher, lesson_id, session_id
):
    """Teacher-facing filter: ?question_kind=bug_hunt (or quiz) imports only
    that kind from a mixed lesson, so a teacher can build a bugs-only or
    quiz-only session from a lesson that has both."""
    _, headers = teacher
    db_session.add(LessonQuestion(
        lesson_id=lesson_id, question_text="Python nima?",
        options=["Til", "Ilon", "Kitob", "Fayl"], correct_option=0,
        time_limit=30, points=1000, order_index=0,
    ))
    db_session.add(LessonQuestion(
        lesson_id=lesson_id, question_text="Xato qayerda?",
        time_limit=90, points=1500, order_index=1,
        question_kind="bug_hunt",
        code_snippet="a = 1\nb = 2\nprint(a - b)",
        code_language="python",
        bug_line=3,
        distractor_lines=[1, 2],
        bug_explanation="+ bo'lishi kerak edi",
    ))
    await db_session.commit()

    resp = await async_client.post(
        f"{BASE}/{session_id}/import-questions",
        params={"lesson_id": lesson_id, "question_kind": "bug_hunt"},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 1
    assert data[0]["question_kind"] == "bug_hunt"


async def test_import_question_kind_invalid_value_rejected(
    async_client: AsyncClient, teacher, lesson_id, session_id
):
    _, headers = teacher
    resp = await async_client.post(
        f"{BASE}/{session_id}/import-questions",
        params={"lesson_id": lesson_id, "question_kind": "not_a_kind"},
        headers=headers,
    )
    assert resp.status_code == 400


async def test_import_quiz_only_lesson_unaffected_by_bug_hunt_branch(
    async_client: AsyncClient, db_session, teacher, lesson_id, session_id
):
    """Regression check: splitting the import loop into quiz/bug_hunt
    branches must not change quiz-only import behavior."""
    _, headers = teacher
    db_session.add(LessonQuestion(
        lesson_id=lesson_id, question_text="1 + 1 nechiga teng?",
        options=["1", "2", "3", "4"], correct_option=1,
        time_limit=20, points=500, order_index=0,
    ))
    await db_session.commit()

    resp = await async_client.post(
        f"{BASE}/{session_id}/import-questions",
        params={"lesson_id": lesson_id},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 1
    assert data[0]["question_kind"] == "quiz"
    assert data[0]["options"][data[0]["correct_option"]] == "2"
