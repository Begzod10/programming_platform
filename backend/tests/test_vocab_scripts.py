"""The two one-off backfill scripts: build vocabulary for lessons that have none, and seed the dictionaries of
students who finished lessons before auto-seeding existed. Both must be safe to stop, re-run and dry-run."""
import json

import pytest_asyncio

from app.db.database import AsyncSessionLocal
from app.models.lesson import LessonCompletion
from app.services import lesson_vocab_ai_service as ai_svc
from app.services.grok_ai_client import ProviderError
from scripts import generate_lesson_vocabulary as gen
from scripts import seed_vocab_for_completed as seed
from tests import _vocab_helpers as H


@pytest_asyncio.fixture(autouse=True)
async def _cleanup():
    yield
    await H.cleanup()


def _ai(monkeypatch, *, fail_on=()):
    """call_chain stand-in: three terms named after the lesson title; ProviderError for titles in `fail_on`."""
    calls = []

    async def fake(prompt, max_tokens, validator=None, json_mode=True):
        title = next(line[6:] for line in prompt.splitlines() if line.startswith("Dars: "))
        calls.append(title)
        if title in fail_on:
            raise ProviderError("down")
        text = json.dumps({"terms": [{"word": f"{title} t{i}", "definition_uz": "uz", "definition_ru": "ru"}
                                     for i in range(3)]})
        return text, validator(text), "fake", []

    monkeypatch.setattr(ai_svc, "call_chain", fake)
    return calls


async def _course(lessons=3):
    tid = await H.make_user(teacher=True)
    cid, lids = await H.make_course(tid, lessons=lessons)
    return tid, cid, lids


async def test_generate_script_only_lessons_without_words(monkeypatch):
    _, cid, lids = await _course()
    await H.add_word(lids[0], "selector", "tanlagich")
    calls = _ai(monkeypatch)
    out = await gen.run(dry_run=False, limit=None, course_ids=[cid], sleep=0)
    assert out == {"lessons": 2, "terms": 6, "skipped": 0, "failed": 0, "aborted": False}
    assert calls == ["Selektorlar 1", "Selektorlar 2"]
    assert [w.word for w in await H.words(lids[0])] == ["selector"]
    assert len(await H.words(lids[1])) == 3


async def test_generate_script_continues_after_failure_and_is_resumable(monkeypatch):
    _, cid, lids = await _course()
    _ai(monkeypatch, fail_on={"Selektorlar 1"})
    out = await gen.run(dry_run=False, limit=None, course_ids=[cid], sleep=0)
    assert out == {"lessons": 2, "terms": 6, "skipped": 0, "failed": 1, "aborted": False}
    assert await H.words(lids[1]) == [] and len(await H.words(lids[2])) == 3
    calls = _ai(monkeypatch)                                    # second run: only the lesson that failed is left
    out = await gen.run(dry_run=False, limit=None, course_ids=[cid], sleep=0)
    assert out == {"lessons": 1, "terms": 3, "skipped": 0, "failed": 0, "aborted": False} and calls == ["Selektorlar 1"]
    out = await gen.run(dry_run=False, limit=None, course_ids=[cid], sleep=0)
    assert out == {"lessons": 0, "terms": 0, "skipped": 0, "failed": 0, "aborted": False}


async def test_generate_script_dry_run_writes_nothing(monkeypatch):
    _, cid, lids = await _course(lessons=2)
    _ai(monkeypatch)
    out = await gen.run(dry_run=True, limit=None, course_ids=[cid], sleep=0)
    assert out == {"lessons": 2, "terms": 6, "skipped": 0, "failed": 0, "aborted": False}
    assert await H.words(lids[0]) == [] and await H.words(lids[1]) == []


async def test_generate_script_limit_and_short_lessons(monkeypatch):
    tid = await H.make_user(teacher=True)
    cid, lids = await H.make_course(tid, lessons=2, text="Qisqa.")
    calls = _ai(monkeypatch)
    out = await gen.run(dry_run=False, limit=None, course_ids=[cid], sleep=0)
    assert out == {"lessons": 0, "terms": 0, "skipped": 2, "failed": 0, "aborted": False} and calls == []
    _, cid2, _ = await _course(lessons=3)
    out = await gen.run(dry_run=False, limit=2, course_ids=[cid2], sleep=0)
    assert out["lessons"] == 2 and len(calls) == 2


async def test_generate_script_ignores_inactive_lessons(monkeypatch):
    tid = await H.make_user(teacher=True)
    cid, _ = await H.make_course(tid, is_active=False)
    calls = _ai(monkeypatch)
    out = await gen.run(dry_run=False, limit=None, course_ids=[cid], sleep=0)
    assert out["lessons"] == 0 and calls == []


async def _finished(lessons=2):
    """A student who finished `lessons` lessons; each lesson has 'selector' and a word of its own."""
    tid, sid = await H.make_user(teacher=True), await H.make_user()
    cid, lids = await H.make_course(tid, lessons=lessons)
    async with AsyncSessionLocal() as db:
        for lid in lids:
            db.add(LessonCompletion(student_id=sid, lesson_id=lid))
        await db.commit()
    for i, lid in enumerate(lids):
        await H.add_word(lid, "selector", "tanlagich", "селектор")
        await H.add_word(lid, f"word{i}", "ta'rif", None, order=1)
    return sid, cid, lids


async def test_seed_script_counts_rows_in_dry_run_without_writing():
    sid, cid, _ = await _finished()
    out = await seed.run(dry_run=True, limit=None, course_ids=[cid])
    assert out == {"pairs": 2, "rows": 3, "failed": 0}   # selector once (both lessons share it) + word0 + word1
    assert await H.dict_rows(sid) == []


async def test_seed_script_seeds_completed_lessons_and_is_idempotent():
    sid, cid, _ = await _finished()
    assert await seed.run(dry_run=False, limit=None, course_ids=[cid]) == {"pairs": 2, "rows": 3, "failed": 0}
    assert sorted((r.word, r.lang) for r in await H.dict_rows(sid)) == [
        ("selector", "uz"), ("word0", "uz"), ("word1", "uz")]
    assert await seed.run(dry_run=False, limit=None, course_ids=[cid]) == {"pairs": 2, "rows": 0, "failed": 0}
    assert len(await H.dict_rows(sid)) == 3


async def test_seed_script_skips_lessons_without_words_and_honours_limit():
    tid, sid = await H.make_user(teacher=True), await H.make_user()
    cid, lids = await H.make_course(tid, lessons=3)
    async with AsyncSessionLocal() as db:
        for lid in lids:
            db.add(LessonCompletion(student_id=sid, lesson_id=lid))
        await db.commit()
    await H.add_word(lids[0], "a", "x")
    await H.add_word(lids[2], "b", "y")
    assert await seed.run(dry_run=True, limit=None, course_ids=[cid]) == {"pairs": 2, "rows": 2, "failed": 0}
    assert await seed.run(dry_run=False, limit=1, course_ids=[cid]) == {"pairs": 1, "rows": 1, "failed": 0}


async def test_seed_script_counts_failures_and_keeps_going(monkeypatch):
    from app.services import vocab_seed_service
    sid, cid, lids = await _finished()
    real = vocab_seed_service._new_rows

    def flaky(student_id, lesson_id, *a, **k):
        if lesson_id == lids[0]:
            raise RuntimeError("boom")
        return real(student_id, lesson_id, *a, **k)

    monkeypatch.setattr(vocab_seed_service, "_new_rows", flaky)
    assert await seed.run(dry_run=False, limit=None, course_ids=[cid]) == {"pairs": 2, "rows": 2, "failed": 1}


async def test_generate_script_stops_after_repeated_failures(monkeypatch):
    _, cid, lids = await _course(lessons=8)
    calls = _ai(monkeypatch, fail_on={f"Selektorlar {i}" for i in range(8)})
    out = await gen.run(dry_run=False, limit=None, course_ids=[cid], sleep=0)
    assert out["failed"] == gen.MAX_CONSECUTIVE_FAILURES == 5 and len(calls) == 5
    assert out["aborted"] is True


async def test_generate_script_survives_an_unexpected_error_on_one_lesson(monkeypatch):
    _, cid, lids = await _course(lessons=2)
    _ai(monkeypatch)
    real = gen.generate_for_lesson

    async def flaky(db, lesson_id, **kw):
        if lesson_id == lids[0]:
            raise LookupError("lesson vanished")
        return await real(db, lesson_id, **kw)

    monkeypatch.setattr(gen, "generate_for_lesson", flaky)
    out = await gen.run(dry_run=False, limit=None, course_ids=[cid], sleep=0)
    assert (out["lessons"], out["failed"]) == (1, 1)
