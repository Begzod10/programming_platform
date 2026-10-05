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


# ── duplicate content across students / .txt hint ─────────────────────────────

from app.services.integrity_check import content_fingerprint  # noqa: E402

def _unique_page() -> str:
    """A fresh page per test: committed rows persist across tests in the shared
    test DB, so a fixed page would match another test's project."""
    tag = uuid.uuid4().hex
    return "<!DOCTYPE html>\n<html>\n<body>\n" + "\n".join(
        f"  <p class=\"row{i}\">Qator raqami {i} {tag} uchun uzun matn</p>" for i in range(20)
    ) + "\n</body>\n</html>"


def _snapshot(path, body):
    return f"### {path}\n```\n{body}\n```"


def test_fingerprint_ignores_file_names_whitespace_case_and_order():
    _PAGE = _unique_page()
    a = _snapshot("Новая папка/index.html", _PAGE) + "\n\n" + _snapshot("style.css", "body { color: red; }" * 20)
    b = _snapshot("style.css", "BODY {  color:  red; }" * 20 + "") + "\n\n" + _snapshot(
        "hw/INDEX.HTML", _PAGE.replace("\n", "\n    "))
    assert content_fingerprint(a) is not None
    assert content_fingerprint(a) == content_fingerprint(b)


def test_fingerprint_differs_for_different_code_and_is_none_for_tiny_code():
    _PAGE = _unique_page()
    assert content_fingerprint(_snapshot("a.html", _PAGE)) != content_fingerprint(
        _snapshot("a.html", _PAGE.replace("Qator", "Boshqa")))
    assert content_fingerprint(_snapshot("a.html", "<h1>Hi</h1>")) is None


async def _other_student(async_client) -> int:
    uid = uuid.uuid4().hex[:8]
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"username": f"integ2_{uid}", "email": f"integ2_{uid}@example.com",
              "password": "securepass123"},
    )
    assert reg.status_code == 201, reg.text
    return reg.json()["user"]["id"]


async def test_same_code_from_another_student_is_held(async_client, db_session, student_id):
    _PAGE = _unique_page()
    text = _snapshot("index.html", _PAGE)
    other = await _other_student(async_client)
    first = await _project(db_session, other, submitted_ago=timedelta(hours=3))
    r1 = await check_submission_integrity(db_session, first, files_included=["index.html"], content_text=text)
    assert not r1.held                      # the first one in is not a duplicate of anything
    await db_session.commit()

    second = await _project(db_session, student_id, submitted_ago=timedelta(0))
    r2 = await check_submission_integrity(
        db_session, second, files_included=["folder/index.html"],
        content_text=_snapshot("folder/index.html", _PAGE.replace("\n", "\n  ")))
    assert r2.held
    assert [t["code"] for t in r2.triggers] == ["duplicate_content"]
    assert f"#{first.id}" in r2.feedback()


async def test_same_students_own_resubmission_is_not_a_duplicate(db_session, student_id):
    _PAGE = _unique_page()
    text = _snapshot("index.html", _PAGE)
    first = await _project(db_session, student_id, submitted_ago=timedelta(hours=3))
    await check_submission_integrity(db_session, first, files_included=["index.html"], content_text=text)
    await db_session.commit()
    again = await _project(db_session, student_id, submitted_ago=timedelta(0))
    r = await check_submission_integrity(db_session, again, files_included=["index.html"], content_text=text)
    assert not r.held


async def test_plain_text_hold_tells_the_student_what_to_fix(db_session, student_id):
    p = await _project(db_session, student_id, submitted_ago=timedelta(0))
    r = await check_submission_integrity(
        db_session, p, files_included=["Новая папка/diyor.html.txt"], content_text="<h1>x</h1>")
    fb = r.feedback()
    assert "diyor.html.txt" in fb
    assert "kengaytmani" in fb          # uz hint
    assert "переименуйте" in fb         # ru hint
    assert "O'qituvchi uchun" in fb     # teacher section still there
