"""Tests for sample_copy_check.py — the deterministic "is this submission
just the lesson's own sample project, copied" guard in the AI review
pipeline (see ai_review_service.run_ai_review_for_project).

Two layers:
  1. Pure unit tests of check_against_sample() — no DB, no mocking, fast.
  2. An integration test through run_ai_review_for_project() proving the
     guard actually short-circuits the pipeline (never calls the AI, never
     approves) when a submission matches a lesson's LessonSample, and
     leaves a genuinely different submission to the normal AI path.
"""
import uuid
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from app.services.sample_copy_check import (
    MIN_COMPARISON_LENGTH,
    check_against_sample,
)

# A realistic-length snippet — long enough to clear MIN_COMPARISON_LENGTH
# on its own so tests don't accidentally fall into the "too short to judge"
# branch.
_HTML_SAMPLE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <title>Mening sahifam</title>
</head>
<body>
    <header class="site-header">
        <h1>Salom, dunyo!</h1>
        <nav>
            <a href="#home">Bosh sahifa</a>
            <a href="#about">Biz haqimizda</a>
            <a href="#contact">Aloqa</a>
        </nav>
    </header>
    <main>
        <p>Bu mening birinchi HTML sahifam. Bu yerda men o'zim haqimda yozaman.</p>
    </main>
</body>
</html>
"""

_UNRELATED_TEXT = """
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


class Calculator:
    def add(self, x, y):
        return x + y

    def subtract(self, x, y):
        return x - y
"""


# ── Pure unit tests ──────────────────────────────────────────────────────────

def test_identical_text_is_flagged_as_copy():
    # Arrange / Act
    result = check_against_sample(_HTML_SAMPLE, _HTML_SAMPLE)

    # Assert
    assert result.available is True
    assert result.ratio == pytest.approx(1.0, abs=0.01)
    assert result.is_copy is True


def test_reformatted_whitespace_still_counts_as_copy():
    """Copy-paste followed by re-indenting/reformatting must not slip past
    the check — only structure/logic should matter, not literal whitespace."""
    reformatted = "\n".join(
        f"    {line.strip()}" for line in _HTML_SAMPLE.strip().splitlines()
    )

    result = check_against_sample(reformatted, _HTML_SAMPLE)

    assert result.is_copy is True


def test_unrelated_code_is_not_flagged():
    # Arrange / Act
    result = check_against_sample(_UNRELATED_TEXT, _HTML_SAMPLE)

    # Assert
    assert result.available is True
    assert result.ratio < 0.5
    assert result.is_copy is False


def test_wrapped_in_repo_snapshot_markup_still_matches():
    """github_repo_service wraps each file as '### path\\n```\\n{code}\\n```'
    — the noise-stripping normalizer must see through that wrapper to the
    actual code underneath."""
    wrapped = f"### index.html\n```\n{_HTML_SAMPLE}\n```"

    result = check_against_sample(wrapped, _HTML_SAMPLE)

    assert result.is_copy is True


def test_no_sample_code_means_unavailable():
    result = check_against_sample(_HTML_SAMPLE, None)

    assert result.available is False
    assert result.is_copy is False


def test_empty_submission_means_unavailable():
    result = check_against_sample("", _HTML_SAMPLE)

    assert result.available is False


def test_short_snippets_are_never_flagged_even_if_identical():
    """A one-line lesson ("<h1>Salom</h1>") has essentially one correct
    answer — every genuine student would score "identical" to the sample.
    Below MIN_COMPARISON_LENGTH the check must refuse to judge at all."""
    short = "<h1>Salom</h1>"
    assert len(short) < MIN_COMPARISON_LENGTH

    result = check_against_sample(short, short)

    assert result.available is False
    assert result.is_copy is False


def test_partial_overlap_below_threshold_is_not_flagged():
    """Genuinely inspired-but-different work (reuses some structure, adds a
    lot of original content) must not get caught by a guard meant for
    verbatim copies."""
    extended = _HTML_SAMPLE + "\n" + _UNRELATED_TEXT * 2

    result = check_against_sample(extended, _HTML_SAMPLE)

    assert result.available is True
    assert result.is_copy is False


# ── Integration: run_ai_review_for_project short-circuits on a copy ────────

@pytest_asyncio.fixture
async def lesson_with_sample(db_session):
    """A Course + Lesson + LessonSample whose html_code is _HTML_SAMPLE, plus
    a teacher-role Student to own the course (courses.instructor_id FK)."""
    from app.models.course import Course
    from app.models.lesson import Lesson
    from app.models.lesson_sample import LessonSample
    from app.models.user import Student, UserRole

    uid = uuid.uuid4().hex[:8]
    instructor = Student(
        username=f"copychk_teacher_{uid}",
        email=f"copychk_teacher_{uid}@example.com",
        hashed_password="hashed",
        role=UserRole.teacher,
    )
    db_session.add(instructor)
    await db_session.flush()

    course = Course(
        title="Test HTML course",
        description="d",
        instructor_id=instructor.id,
        difficulty_level="Easy",
        duration_weeks=1,
        max_points=100,
    )
    db_session.add(course)
    await db_session.flush()

    lesson = Lesson(
        course_id=course.id,
        title="Birinchi sahifa",
        task_title="HTML sahifa yasang",
        task_description="Sarlavha va navigatsiya bilan sahifa yozing.",
        task_technologies="HTML",
        code_language="HTML",
    )
    db_session.add(lesson)
    await db_session.flush()

    sample = LessonSample(
        lesson_id=lesson.id,
        title="Namuna",
        sample_type="web",
        html_code=_HTML_SAMPLE,
    )
    db_session.add(sample)
    await db_session.commit()
    await db_session.refresh(lesson)

    return lesson


@pytest_asyncio.fixture
async def student_project_for_lesson(db_session, lesson_with_sample):
    """A student's Project + Submission linked to lesson_with_sample."""
    from app.models.project import Project
    from app.models.submission import Submission
    from app.models.user import Student

    uid = uuid.uuid4().hex[:8]
    student = Student(
        username=f"copychk_student_{uid}",
        email=f"copychk_student_{uid}@example.com",
        hashed_password="hashed",
    )
    db_session.add(student)
    await db_session.flush()

    project = Project(
        student_id=student.id,
        title="Mening loyiham",
        description="d",
        difficulty_level="Easy",
        github_url="https://github.com/example/repo",
        status="Submitted",
    )
    db_session.add(project)
    await db_session.flush()

    db_session.add(Submission(
        project_id=project.id,
        student_id=student.id,
        lesson_id=lesson_with_sample.id,
        github_url=project.github_url,
        status="Submitted",
    ))
    await db_session.commit()
    await db_session.refresh(project)

    return project


def _mock_snapshot(content_text: str) -> dict:
    return {
        "exists": True,
        "default_branch": "main",
        "file_count": 1,
        "files_included": ["index.html"],
        "content_text": content_text,
        "truncated": False,
        "error": None,
        "authorship": {"available": False, "reason": "mocked"},
    }


@pytest.mark.asyncio
async def test_copied_sample_is_rejected_without_calling_ai(
    db_session, student_project_for_lesson
):
    """The core bug report: submitting the lesson's own sample project
    verbatim must NOT pass — and must not even spend an AI call doing it."""
    from app.services.ai_review_service import run_ai_review_for_project

    ai_mock = AsyncMock(return_value={"grade": "A", "points": 95})
    with patch(
        "app.services.ai_review_service.fetch_github_snapshot",
        new=AsyncMock(return_value=_mock_snapshot(_HTML_SAMPLE)),
    ), patch(
        "app.services.ai_review_service.analyze_project_with_grok",
        new=ai_mock,
    ):
        result = await run_ai_review_for_project(
            db_session, student_project_for_lesson, raise_on_error=False,
        )

    assert result["success"] is True
    assert result["points"] == 0
    assert result["grade"] == "F"
    assert result["sample_copy_flagged"] is True
    ai_mock.assert_not_called()

    await db_session.refresh(student_project_for_lesson)
    assert student_project_for_lesson.status == "Rejected"
    assert student_project_for_lesson.points_earned == 0
    assert student_project_for_lesson.reviewed_at is not None


@pytest.mark.asyncio
async def test_genuinely_different_submission_still_goes_through_ai(
    db_session, student_project_for_lesson
):
    """A real, independently-written solution for the same lesson must not
    be caught by the copy guard — it should reach the AI grader as normal."""
    from app.services.ai_review_service import run_ai_review_for_project

    ai_mock = AsyncMock(return_value={"grade": "B", "points": 80})
    with patch(
        "app.services.ai_review_service.fetch_github_snapshot",
        new=AsyncMock(return_value=_mock_snapshot(_UNRELATED_TEXT)),
    ), patch(
        "app.services.ai_review_service.analyze_project_with_grok",
        new=ai_mock,
    ):
        result = await run_ai_review_for_project(
            db_session, student_project_for_lesson, raise_on_error=False,
        )

    assert result["success"] is True
    ai_mock.assert_called_once()

    await db_session.refresh(student_project_for_lesson)
    assert student_project_for_lesson.status == "Approved"
    assert student_project_for_lesson.points_earned == 80


@pytest.mark.asyncio
async def test_lesson_without_a_sample_skips_the_guard_entirely(db_session):
    """No LessonSample row at all (the common case — most lessons don't
    have one) must never block a submission; it just goes straight to AI."""
    from app.models.course import Course
    from app.models.lesson import Lesson
    from app.models.project import Project
    from app.models.submission import Submission
    from app.models.user import Student, UserRole
    from app.services.ai_review_service import run_ai_review_for_project

    uid = uuid.uuid4().hex[:8]
    instructor = Student(
        username=f"nosample_teacher_{uid}", email=f"nosample_teacher_{uid}@example.com",
        hashed_password="hashed", role=UserRole.teacher,
    )
    db_session.add(instructor)
    await db_session.flush()
    course = Course(
        title="No sample course", description="d", instructor_id=instructor.id,
        difficulty_level="Easy", duration_weeks=1, max_points=100,
    )
    db_session.add(course)
    await db_session.flush()
    lesson = Lesson(course_id=course.id, title="No sample lesson")
    db_session.add(lesson)
    await db_session.flush()

    student = Student(
        username=f"nosample_student_{uid}", email=f"nosample_student_{uid}@example.com",
        hashed_password="hashed",
    )
    db_session.add(student)
    await db_session.flush()
    project = Project(
        student_id=student.id, title="p", description="d", difficulty_level="Easy",
        github_url="https://github.com/example/repo2", status="Submitted",
    )
    db_session.add(project)
    await db_session.flush()
    db_session.add(Submission(
        project_id=project.id, student_id=student.id, lesson_id=lesson.id,
        github_url=project.github_url, status="Submitted",
    ))
    await db_session.commit()
    await db_session.refresh(project)

    ai_mock = AsyncMock(return_value={"grade": "A", "points": 90})
    with patch(
        "app.services.ai_review_service.fetch_github_snapshot",
        new=AsyncMock(return_value=_mock_snapshot(_HTML_SAMPLE)),
    ), patch(
        "app.services.ai_review_service.analyze_project_with_grok",
        new=ai_mock,
    ):
        await run_ai_review_for_project(db_session, project, raise_on_error=False)

    ai_mock.assert_called_once()
