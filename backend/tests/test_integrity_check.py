"""
Tests for services/integrity_check.py and its hook in run_ai_review_for_project.

A lesson project submitted in a burst (3rd+ within 20 min) or as plain .txt
must be held for a teacher — never sent to the AI grader, never auto-graded.
Teacher-triggered regrades (skip_integrity_check=True) bypass the hold.
The AI call is always mocked.
"""

import uuid
from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from httpx import AsyncClient

from app.models.project import Project
from app.services.integrity_check import check_submission_integrity
from app.utils.datetime_utils import utcnow

BANNERS = "\n".join(f"/* ===== SECTION {i} ===== */" for i in range(6))


@pytest_asyncio.fixture
async def student_id(async_client: AsyncClient) -> int:
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": f"integ_{uid}", "email": f"integ_{uid}@example.com",
              "password": "securepass123"},
    )
    assert reg.status_code == 201, reg.text
    return reg.json()["user"]["id"]


async def _project(db, student_id, *, submitted_ago=None, **kw) -> Project:
    p = Project(
        student_id=student_id, title="Lesson project", description="desc",
        difficulty_level="Easy", status="Submitted",
        submitted_at=(utcnow() - submitted_ago) if submitted_ago is not None else None,
        **kw,
    )
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


# ── check_submission_integrity ────────────────────────────────────────────────

async def test_single_html_submission_is_not_held(db_session, student_id):
    p = await _project(db_session, student_id, submitted_ago=timedelta(0))
    r = await check_submission_integrity(
        db_session, p, files_included=["index.html", "style.css"], content_text="<h1>Hi</h1>")
    assert not r.held
    assert r.feedback() is None


async def test_third_project_within_window_is_held(db_session, student_id):
    await _project(db_session, student_id, submitted_ago=timedelta(minutes=2))
    await _project(db_session, student_id, submitted_ago=timedelta(minutes=5))
    p = await _project(db_session, student_id, submitted_ago=timedelta(0))
    r = await check_submission_integrity(
        db_session, p, files_included=["index.html"], content_text="")
    assert r.held
    assert [t["code"] for t in r.triggers] == ["burst"]


async def test_second_project_or_old_ones_do_not_count_as_burst(db_session, student_id):
    await _project(db_session, student_id, submitted_ago=timedelta(minutes=3))
    await _project(db_session, student_id, submitted_ago=timedelta(hours=2))
    await _project(db_session, student_id)  # draft, never submitted
    p = await _project(db_session, student_id, submitted_ago=timedelta(0))
    r = await check_submission_integrity(
        db_session, p, files_included=["index.html"], content_text="")
    assert not r.held


async def test_plain_text_only_zip_is_held(db_session, student_id):
    p = await _project(db_session, student_id, submitted_ago=timedelta(0))
    r = await check_submission_integrity(
        db_session, p, files_included=["текст 2.txt"], content_text=BANNERS)
    assert r.held
    assert [t["code"] for t in r.triggers] == ["plain_text_only"]
    # Banner style is recorded as a note, and the teacher sees both.
    assert [n["code"] for n in r.notes] == ["ai_style_banners"]
    fb = r.feedback()
    assert "текст 2.txt" in fb and "bo'lim sarlavhasi" in fb


async def test_banners_alone_never_hold(db_session, student_id):
    p = await _project(db_session, student_id, submitted_ago=timedelta(0))
    r = await check_submission_integrity(
        db_session, p, files_included=["index.html"], content_text=BANNERS)
    assert not r.held


# ── run_ai_review_for_project hook ────────────────────────────────────────────

SNAPSHOT_TXT = {
    "exists": True, "files_included": ["текст.txt"], "content_text": "<html></html>",
    "file_count": 1, "truncated": False, "default_branch": "(zip)", "error": None,
}
GOOD_REVIEW = {"grade": "A", "points": 90, "feedback": "ok", "strengths": [],
               "improvements": [], "bugs": [], "summary": "ok", "provider": "mock"}


def _patches(grok):
    svc = "app.services.ai_review_service"
    return (
        patch(f"{svc}.load_lesson_context_for_project",
              AsyncMock(return_value={"lesson_id": None, "course_id": None})),
        patch(f"{svc}.fetch_zip_snapshot", return_value=SNAPSHOT_TXT),
        patch(f"{svc}.load_lesson_sample_code", AsyncMock(return_value=None)),
        patch(f"{svc}.analyze_project_with_grok", grok),
    )


async def test_held_project_is_not_sent_to_ai_and_stays_submitted(db_session, student_id):
    from app.services.ai_review_service import run_ai_review_for_project

    p = await _project(db_session, student_id, submitted_ago=timedelta(0),
                       project_files="/uploads/projects/x.zip")
    grok = AsyncMock(return_value=GOOD_REVIEW)
    a, b, c, d = _patches(grok)
    with a, b, c, d:
        result = await run_ai_review_for_project(db_session, p, raise_on_error=False)

    grok.assert_not_called()
    assert result["success"] is False and result["http_status"] == 409
    await db_session.refresh(p)
    assert p.status == "Submitted"
    assert p.reviewed_at is None and p.grade is None and (p.points_earned or 0) == 0
    assert "o'qituvchi tomonidan tekshiriladi" in p.instructor_feedback


async def test_teacher_regrade_skips_the_hold(db_session, student_id):
    from app.services.ai_review_service import run_ai_review_for_project

    p = await _project(db_session, student_id, submitted_ago=timedelta(0),
                       project_files="/uploads/projects/x.zip")
    grok = AsyncMock(return_value=GOOD_REVIEW)
    a, b, c, d = _patches(grok)
    with a, b, c, d:
        result = await run_ai_review_for_project(
            db_session, p, raise_on_error=False, skip_integrity_check=True)

    grok.assert_called_once()
    assert result["success"] is True
    await db_session.refresh(p)
    assert p.status == "Approved" and p.grade == "A"
