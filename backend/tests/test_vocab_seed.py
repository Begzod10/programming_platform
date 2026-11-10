"""Finishing a lesson puts its vocabulary into the student's dictionary — ONE row per word, in the student's own
language — by every route a lesson can be finished. See docs/superpowers/specs/2026-11-09-lesson-vocabulary-design.md §3.4."""
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.models.dictionary import UserDictionary
from app.models.exercise import Exercise
from app.models.lesson import Lesson, LessonCompletion
from app.models.project import Project
from app.models.submission import Submission
from app.models.user import Student
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
    return await seed_lesson_words(sid, lid)


async def _set_lang(sid, lang):
    async with AsyncSessionLocal() as db:
        (await db.get(Student, sid)).ui_lang = lang
        await db.commit()


def _shape(rows):
    return [(r.word, r.lang, r.context, r.lesson_id) for r in rows]


def _expected(lid):
    """What an Uzbek-language student gets: one row per word."""
    return [("property", "uz", "xossa", lid), ("selector", "uz", "tanlagich", lid)]


# ── the service ─────────────────────────────────────────────────────────────

async def test_uzbek_student_gets_one_uzbek_row_per_word():
    _, sid, _, lid = await _world()
    assert await _seed(sid, lid) == 2
    rows = await H.dict_rows(sid)
    assert _shape(rows) == _expected(lid)
    assert all(r.seeded is True for r in rows)


async def test_russian_student_gets_russian_rows_with_uzbek_text_where_there_is_no_russian():
    _, sid, _, lid = await _world()
    await _set_lang(sid, "ru")
    assert await _seed(sid, lid) == 2
    assert _shape(await H.dict_rows(sid)) == [("property", "ru", "xossa", lid), ("selector", "ru", "селектор", lid)]


async def test_language_falls_back_to_what_the_students_own_dictionary_is_in():
    _, sid, _, lid = await _world()
    async with AsyncSessionLocal() as db:
        db.add_all([UserDictionary(student_id=sid, word=f"mine{i}", context="x", lang="ru") for i in range(2)])
        db.add(UserDictionary(student_id=sid, word="other", context="x", lang="uz"))
        await db.commit()
    assert await _seed(sid, lid) == 2
    seeded = [r for r in await H.dict_rows(sid) if r.seeded]
    assert {r.lang for r in seeded} == {"ru"}


async def test_unknown_stored_language_is_ignored():
    _, sid, _, lid = await _world()
    await _set_lang(sid, "en")
    await _seed(sid, lid)
    assert {r.lang for r in await H.dict_rows(sid)} == {"uz"}


async def test_new_rows_start_as_fresh_review_cards():
    _, sid, _, lid = await _world()
    await _seed(sid, lid)
    r = (await H.dict_rows(sid))[0]
    assert (r.review_count, r.correct_count, r.incorrect_count, r.reps, r.interval_days) == (0, 0, 0, 0, 0)
    assert r.ease_factor == 2.5 and r.next_review_at is None


async def test_idempotent_no_duplicates():
    _, sid, _, lid = await _world()
    assert await _seed(sid, lid) == 2
    assert await _seed(sid, lid) == 0
    assert len(await H.dict_rows(sid)) == 2


async def test_word_the_student_already_has_in_any_language_is_left_alone():
    """Never a second row for a word: two rows of one word are two separate review cards (see practice_words)."""
    _, sid, _, lid = await _world()
    async with AsyncSessionLocal() as db:
        db.add(UserDictionary(student_id=sid, word="Selector", context="сам написал", lang="ru", review_count=7))
        await db.commit()
    assert await _seed(sid, lid) == 1
    rows = {r.word: r for r in await H.dict_rows(sid)}
    assert set(rows) == {"Selector", "property"}
    assert rows["Selector"].context == "сам написал" and rows["Selector"].review_count == 7
    assert rows["Selector"].seeded is False


async def test_duplicate_words_on_the_lesson_seed_once():
    _, sid, _, lid = await _world()
    await H.add_word(lid, "SELECTOR", "takror", "повтор", order=2)
    assert await _seed(sid, lid) == 2
    assert len(await H.dict_rows(sid)) == 2


async def test_long_term_is_cut_to_the_dictionary_width():
    _, sid, _, lid = await _world()
    await H.add_word(lid, "w" * 120, "uzun", None, order=3)          # user_dictionary.word is String(80)
    assert await _seed(sid, lid) == 3
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


def _break_seeding(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("db exploded")
    monkeypatch.setattr(vocab_seed_service, "_new_rows", boom)


async def test_seed_failure_returns_zero_and_does_not_raise(monkeypatch):
    _, sid, _, lid = await _world()
    _break_seeding(monkeypatch)
    assert await _seed(sid, lid) == 0
    assert await H.dict_rows(sid) == []


# ── a finished lesson is one review card per word, and reviewing it clears it ──

async def test_reviewed_words_leave_the_due_queue(async_client):
    tid, sid = await H.make_user(teacher=True), await H.make_user()
    cid, (lid,) = await H.make_course(tid)
    for i in range(4):
        await H.add_word(lid, f"term{i}", f"ta'rif {i}", f"определение {i}", order=i)
    assert await _seed(sid, lid) == 4
    P = "/api/v1/dictionary/practice"
    r = await async_client.get(f"{P}/due-counts", headers=H.h(sid))
    assert (r.json()["due"], r.json()["total"]) == (4, 4)
    r = await async_client.get(f"{P}/words?lang=uz&due_only=true&count=10", headers=H.h(sid))
    assert r.status_code == 200 and len(r.json()) == 4, r.text
    for w in r.json():
        ok = await async_client.post(f"{P}/result", headers=H.h(sid),
                                     json={"word_id": w["id"], "was_correct": True, "grade": 2})
        assert ok.status_code == 200, ok.text
    assert (await async_client.get(f"{P}/due-counts", headers=H.h(sid))).json()["due"] == 0
    r = await async_client.get(f"{P}/words?lang=uz&due_only=true&count=10", headers=H.h(sid))
    assert r.status_code == 400                                       # nothing left to drill today


# ── seeded words are not the student's own effort ───────────────────────────

async def test_seeded_words_do_not_count_towards_word_count_achievements():
    from sqlalchemy import delete
    from app.models.achievement import Achievement
    from app.models.student_achievement import StudentAchievement
    from app.services import achievement_service
    _, sid, _, lid = await _world()
    async with AsyncSessionLocal() as db:
        ach = Achievement(name="Lug'atchi", description="2 ta so'z", badge_image_url="x", points_reward=0,
                          criteria_type="word_count", criteria_value=2)
        db.add(ach)
        await db.commit()
        ach_id = ach.id
    try:
        assert await _seed(sid, lid) == 2
        async with AsyncSessionLocal() as db:
            got = await achievement_service.check_and_award_achievements(db, sid)
            assert ach_id not in [a.achievement_id for a in got]
            db.add_all([UserDictionary(student_id=sid, word=f"own{i}", context="x", lang="uz") for i in range(2)])
            await db.commit()
            got = await achievement_service.check_and_award_achievements(db, sid)
            assert ach_id in [a.achievement_id for a in got]
    finally:
        async with AsyncSessionLocal() as db:
            await db.execute(delete(StudentAchievement).where(StudentAchievement.achievement_id == ach_id))
            await db.execute(delete(Achievement).where(Achievement.id == ach_id))
            await db.commit()


# ── the student's language is remembered from their own requests ────────────

async def test_exercise_submission_remembers_the_students_language(async_client):
    _, sid, cid, lid = await _world()
    async with AsyncSessionLocal() as db:
        ex = Exercise(lesson_id=lid, title="e", description="CSS ___", exercise_type="fill_in_blank",
                      correct_answers="color", points=5)
        db.add(ex)
        await db.commit()
        ex_id = ex.id
    url = f"/api/v1/courses/{cid}/lessons/{lid}/exercises/{ex_id}/submit"
    r = await async_client.post(url, headers=H.h(sid), json={"student_answer": "color", "lang": "ru"})
    assert r.status_code == 200 and r.json()["is_correct"] is True, r.text
    async with AsyncSessionLocal() as db:
        assert (await db.get(Student, sid)).ui_lang == "ru"
    assert _shape(await H.dict_rows(sid)) == [("property", "ru", "xossa", lid), ("selector", "ru", "селектор", lid)]
    r = await async_client.post(url, headers=H.h(sid), json={"student_answer": "color", "lang": "xx"})
    assert r.status_code == 200
    async with AsyncSessionLocal() as db:
        assert (await db.get(Student, sid)).ui_lang == "ru"            # junk does not overwrite it


# ── "+ add to my dictionary" on the lesson card ─────────────────────────────

async def test_add_to_dict_stores_the_readers_language_and_survives_existing_rows(async_client):
    _, sid, cid, lid = await _world()
    vid = (await H.words(lid))[0].id
    url = f"/api/v1/courses/{cid}/lessons/{lid}/vocabulary/{vid}/add-to-dict"
    r = await async_client.post(f"{url}?lang=ru", headers=H.h(sid))
    assert r.status_code == 200 and r.json()["already_exists"] is False, r.text
    assert _shape(await H.dict_rows(sid)) == [("selector", "ru", "селектор", lid)]
    async with AsyncSessionLocal() as db:                              # an old pair of rows for one word
        db.add(UserDictionary(student_id=sid, word="selector", context="eski", lang="uz"))
        await db.commit()
    r = await async_client.post(url, headers=H.h(sid))
    assert r.status_code == 200 and r.json()["already_exists"] is True, r.text
    assert len(await H.dict_rows(sid)) == 2


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
    assert len(await H.dict_rows(sid)) == 2


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
    assert r.status_code == 200 and len(await H.dict_rows(sid)) == 2


async def test_rejected_project_does_not_seed(async_client):
    tid, sid, _, lid = await _world(task_title="Loyiha")
    pid = await _project(sid, lid)
    r = await async_client.post(f"/api/v1/project/{pid}/review", headers=H.h(tid),
                                json={"feedback": "Qayta", "grade": "F", "points": 20, "status": "Rejected"})
    assert r.status_code == 200, r.text
    assert not await _completed(sid, lid) and await H.dict_rows(sid) == []


_SNAPSHOT = {"exists": True, "default_branch": "main", "file_count": 1, "files_included": ["index.html"],
             "content_text": "<h1>Salom</h1>", "truncated": False, "error": None,
             "authorship": {"available": False, "reason": "mocked"}}
_REVIEW = {"grade": "A", "points": 95, "feedback": "Zo'r", "strengths": [], "improvements": [], "bugs": [],
           "summary": "ok", "provider": "fake"}


async def test_completion_via_ai_review_seeds():
    from app.services.ai_review_service import run_ai_review_for_project
    _, sid, _, lid = await _world(task_title="Loyiha")
    pid = await _project(sid, lid)
    async with AsyncSessionLocal() as db:
        project = await db.get(Project, pid)
        with patch("app.services.ai_review_service.fetch_github_snapshot", new=AsyncMock(return_value=_SNAPSHOT)), \
                patch("app.services.ai_review_service.analyze_project_with_grok", new=AsyncMock(return_value=_REVIEW)):
            result = await run_ai_review_for_project(db, project, raise_on_error=False, skip_integrity_check=True)
    assert result["success"] is True and result["points"] == 95, result
    assert await _completed(sid, lid)
    assert _shape(await H.dict_rows(sid)) == _expected(lid)


# ── a seeding failure must not cost anyone their finished lesson (spec §3.4, §3.6) ──

async def test_broken_seeding_does_not_break_the_complete_endpoint(async_client, monkeypatch):
    _, sid, _, lid = await _world()
    _break_seeding(monkeypatch)
    r = await async_client.post(f"/api/v1/lessons/{lid}/complete", headers=H.h(sid))
    assert r.status_code == 200, r.text
    assert await _completed(sid, lid)


async def test_broken_seeding_does_not_break_a_correct_exercise_answer(async_client, monkeypatch):
    _, sid, cid, lid = await _world()
    async with AsyncSessionLocal() as db:
        ex = Exercise(lesson_id=lid, title="e", description="CSS ___", exercise_type="fill_in_blank",
                      correct_answers="color", points=5)
        db.add(ex)
        await db.commit()
        ex_id = ex.id
    _break_seeding(monkeypatch)
    r = await async_client.post(f"/api/v1/courses/{cid}/lessons/{lid}/exercises/{ex_id}/submit", headers=H.h(sid),
                                json={"student_answer": "color"})
    assert r.status_code == 200 and r.json()["is_correct"] is True, r.text
    assert await _completed(sid, lid)


async def test_broken_seeding_does_not_break_manual_project_approval(async_client, monkeypatch):
    tid, sid, _, lid = await _world(task_title="Loyiha")
    pid = await _project(sid, lid)
    _break_seeding(monkeypatch)
    r = await async_client.post(f"/api/v1/project/{pid}/review", headers=H.h(tid),
                                json={"feedback": "Yaxshi", "grade": "A", "points": 90, "status": "Approved"})
    assert r.status_code == 200, r.text
    assert await _completed(sid, lid)


async def test_broken_seeding_does_not_break_the_ai_review(monkeypatch):
    from app.services.ai_review_service import run_ai_review_for_project
    _, sid, _, lid = await _world(task_title="Loyiha")
    pid = await _project(sid, lid)
    _break_seeding(monkeypatch)
    async with AsyncSessionLocal() as db:
        project = await db.get(Project, pid)
        with patch("app.services.ai_review_service.fetch_github_snapshot", new=AsyncMock(return_value=_SNAPSHOT)), \
                patch("app.services.ai_review_service.analyze_project_with_grok", new=AsyncMock(return_value=_REVIEW)):
            result = await run_ai_review_for_project(db, project, raise_on_error=False, skip_integrity_check=True)
        assert result["success"] is True and result["project_id"] == pid, result
    assert await _completed(sid, lid)
