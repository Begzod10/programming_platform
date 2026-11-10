"""Finishing a lesson puts its vocabulary into the student's dictionary (one row per language), by every route a
lesson can be finished. See docs/superpowers/specs/2026-11-09-lesson-vocabulary-design.md §3.4."""
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.models.dictionary import UserDictionary
from app.models.exercise import Exercise
from app.models.lesson import Lesson, LessonCompletion
from app.models.project import Project
from app.models.submission import Submission
from app.services import vocab_seed_service
from app.services.vocab_seed_service import seed_lesson_words
from tests import _vocab_helpers as H


@pytest_asyncio.fixture(autouse=True)
async def _cleanup():
    yield
    await H.cleanup()


async def _world(*, demo=False, **lesson_fields):
    """(teacher_id, student_id, course_id, lesson_id) with two words on the lesson, the second without Russian."""
    tid, sid = await H.make_user(teacher=True), await H.make_user(demo=demo)
    cid, (lid,) = await H.make_course(tid, **lesson_fields)
    await H.enroll(sid, cid)
    await H.add_word(lid, "selector", "tanlagich", "селектор")
    await H.add_word(lid, "property", "xossa", None, order=1)
    return tid, sid, cid, lid


async def _seed(sid, lid):
    async with AsyncSessionLocal() as db:
        return await seed_lesson_words(db, sid, lid)


def _shape(rows):
    return [(r.word, r.lang, r.context, r.lesson_id) for r in rows]


def _expected(lid):
    return [("property", "uz", "xossa", lid), ("selector", "ru", "селектор", lid), ("selector", "uz", "tanlagich", lid)]


# ── the service ─────────────────────────────────────────────────────────────

async def test_seeds_uz_and_ru_rows_and_skips_ru_without_a_definition():
    _, sid, _, lid = await _world()
    assert await _seed(sid, lid) == 3
    assert _shape(await H.dict_rows(sid)) == _expected(lid)


async def test_new_rows_start_as_fresh_review_cards():
    _, sid, _, lid = await _world()
    await _seed(sid, lid)
    r = (await H.dict_rows(sid))[0]
    assert (r.review_count, r.correct_count, r.incorrect_count, r.reps, r.interval_days) == (0, 0, 0, 0, 0)
    assert r.ease_factor == 2.5 and r.next_review_at is None


async def test_idempotent_no_duplicates():
    _, sid, _, lid = await _world()
    assert await _seed(sid, lid) == 3
    assert await _seed(sid, lid) == 0
    assert len(await H.dict_rows(sid)) == 3


async def test_word_the_student_already_has_is_kept_as_is():
    _, sid, _, lid = await _world()
    async with AsyncSessionLocal() as db:
        db.add(UserDictionary(student_id=sid, word="Selector", context="o'zim yozganman", lang="uz", review_count=7))
        await db.commit()
    assert await _seed(sid, lid) == 2
    rows = {(r.word, r.lang): r for r in await H.dict_rows(sid)}
    assert rows[("Selector", "uz")].context == "o'zim yozganman" and rows[("Selector", "uz")].review_count == 7
    assert ("selector", "uz") not in rows and ("selector", "ru") in rows and ("property", "uz") in rows


async def test_duplicate_words_on_the_lesson_seed_once():
    _, sid, _, lid = await _world()
    await H.add_word(lid, "SELECTOR", "takror", "повтор", order=2)
    assert await _seed(sid, lid) == 3
    assert len(await H.dict_rows(sid)) == 3


async def test_long_term_is_cut_to_the_dictionary_width():
    _, sid, _, lid = await _world()
    await H.add_word(lid, "w" * 120, "uzun", None, order=3)          # user_dictionary.word is String(80)
    assert await _seed(sid, lid) == 4
    assert max(len(r.word) for r in await H.dict_rows(sid)) == 80


async def test_demo_student_gets_nothing():
    _, sid, _, lid = await _world(demo=True)
    assert await _seed(sid, lid) == 0
    assert await H.dict_rows(sid) == []


async def test_lesson_without_words_and_unknown_ids_return_zero():
    tid, sid = await H.make_user(teacher=True), await H.make_user()
    _, (lid,) = await H.make_course(tid)
    assert await _seed(sid, lid) == 0
    assert await _seed(sid, 987654321) == 0
    assert await _seed(987654321, lid) == 0


async def test_seed_failure_returns_zero_does_not_raise_and_leaves_the_session_usable(monkeypatch):
    _, sid, _, lid = await _world()

    def boom(*a, **k):
        raise RuntimeError("db exploded")

    monkeypatch.setattr(vocab_seed_service, "_new_rows", boom)
    async with AsyncSessionLocal() as db:
        assert await seed_lesson_words(db, sid, lid) == 0
        assert (await db.execute(select(Lesson.id).where(Lesson.id == lid))).scalar() == lid
    assert await H.dict_rows(sid) == []


# ── every way a lesson gets finished ────────────────────────────────────────

async def _completed(sid, lid):
    async with AsyncSessionLocal() as db:
        return (await db.execute(select(LessonCompletion).where(
            LessonCompletion.student_id == sid, LessonCompletion.lesson_id == lid))).scalar_one_or_none() is not None


async def test_completion_via_complete_endpoint_seeds_and_recompleting_does_not_reseed(async_client):
    _, sid, _, lid = await _world()
    r = await async_client.post(f"/api/v1/lessons/{lid}/complete", headers=H.h(sid))
    assert r.status_code == 200, r.text
    assert _shape(await H.dict_rows(sid)) == _expected(lid)
    r = await async_client.post(f"/api/v1/lessons/{lid}/complete", headers=H.h(sid))
    assert r.status_code == 200 and r.json()["already_completed"] is True
    assert len(await H.dict_rows(sid)) == 3


async def test_completion_via_exercises_seeds(async_client):
    _, sid, cid, lid = await _world()
    async with AsyncSessionLocal() as db:
        ex = Exercise(lesson_id=lid, title="e", description="CSS ___", exercise_type="fill_in_blank",
                      correct_answers="color", points=5)
        db.add(ex)
        await db.commit()
        ex_id = ex.id
    r = await async_client.post(f"/api/v1/courses/{cid}/lessons/{lid}/exercises/{ex_id}/submit", headers=H.h(sid),
                                json={"student_answer": "wrong"})
    assert r.status_code == 200, r.text
    assert await H.dict_rows(sid) == []                              # not finished yet
    r = await async_client.post(f"/api/v1/courses/{cid}/lessons/{lid}/exercises/{ex_id}/submit", headers=H.h(sid),
                                json={"student_answer": "color"})
    assert r.status_code == 200 and r.json()["is_correct"] is True, r.text
    assert await _completed(sid, lid)
    assert _shape(await H.dict_rows(sid)) == _expected(lid)


async def _project(sid, lid):
    async with AsyncSessionLocal() as db:
        p = Project(student_id=sid, title="Loyiha", description="d", difficulty_level="Easy",
                    github_url="https://github.com/example/repo", status="Submitted")
        db.add(p)
        await db.flush()
        db.add(Submission(project_id=p.id, student_id=sid, lesson_id=lid, github_url=p.github_url, status="Submitted"))
        await db.commit()
        return p.id


async def test_completion_via_manual_project_approval_seeds(async_client):
    tid, sid, _, lid = await _world(task_title="Loyiha")
    pid = await _project(sid, lid)
    body = {"feedback": "Yaxshi", "grade": "A", "points": 90, "status": "Approved"}
    r = await async_client.post(f"/api/v1/project/{pid}/review", headers=H.h(tid), json=body)
    assert r.status_code == 200, r.text
    assert await _completed(sid, lid)
    assert _shape(await H.dict_rows(sid)) == _expected(lid)
    r = await async_client.post(f"/api/v1/project/{pid}/review", headers=H.h(tid), json=body)   # re-review
    assert r.status_code == 200 and len(await H.dict_rows(sid)) == 3


async def test_rejected_project_does_not_seed(async_client):
    tid, sid, _, lid = await _world(task_title="Loyiha")
    pid = await _project(sid, lid)
    r = await async_client.post(f"/api/v1/project/{pid}/review", headers=H.h(tid),
                                json={"feedback": "Qayta", "grade": "F", "points": 20, "status": "Rejected"})
    assert r.status_code == 200, r.text
    assert not await _completed(sid, lid) and await H.dict_rows(sid) == []


async def test_completion_via_ai_review_seeds():
    from app.services.ai_review_service import run_ai_review_for_project
    _, sid, _, lid = await _world(task_title="Loyiha")
    pid = await _project(sid, lid)
    snapshot = {"exists": True, "default_branch": "main", "file_count": 1, "files_included": ["index.html"],
                "content_text": "<h1>Salom</h1>", "truncated": False, "error": None,
                "authorship": {"available": False, "reason": "mocked"}}
    review = {"grade": "A", "points": 95, "feedback": "Zo'r", "strengths": [], "improvements": [], "bugs": [],
              "summary": "ok", "provider": "fake"}
    async with AsyncSessionLocal() as db:
        project = await db.get(Project, pid)
        with patch("app.services.ai_review_service.fetch_github_snapshot", new=AsyncMock(return_value=snapshot)), \
                patch("app.services.ai_review_service.analyze_project_with_grok", new=AsyncMock(return_value=review)):
            result = await run_ai_review_for_project(db, project, raise_on_error=False, skip_integrity_check=True)
    assert result["success"] is True and result["points"] == 95, result
    assert await _completed(sid, lid)
    assert _shape(await H.dict_rows(sid)) == _expected(lid)
