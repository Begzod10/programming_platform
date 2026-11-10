"""Lesson vocabulary carries a Russian definition and a source (manual | ai).
See docs/superpowers/specs/2026-11-09-lesson-vocabulary-design.md."""
import pytest_asyncio

from tests import _vocab_helpers as H


@pytest_asyncio.fixture(autouse=True)
async def _cleanup():
    yield
    await H.cleanup()


def _url(cid, lid, suffix=""):
    return f"/api/v1/courses/{cid}/lessons/{lid}/vocabulary{suffix}"


async def test_post_vocab_accepts_definition_ru(async_client):
    tid = await H.make_user(teacher=True)
    cid, (lid,) = await H.make_course(tid)
    r = await async_client.post(_url(cid, lid), headers=H.h(tid),
                                json={"word": "selector", "definition": "tanlagich", "definition_ru": "селектор"})
    assert r.status_code == 200, r.text
    assert r.json()["definition_ru"] == "селектор"
    assert r.json()["source"] == "manual"


async def test_post_vocab_without_definition_ru_still_works(async_client):
    tid = await H.make_user(teacher=True)
    cid, (lid,) = await H.make_course(tid)
    r = await async_client.post(_url(cid, lid), headers=H.h(tid), json={"word": "selector", "definition": "tanlagich"})
    assert r.status_code == 200, r.text
    assert r.json()["definition_ru"] is None


async def test_get_vocab_returns_definition_ru(async_client):
    tid, sid = await H.make_user(teacher=True), await H.make_user()
    cid, (lid,) = await H.make_course(tid)
    await H.add_word(lid, "selector", "tanlagich")
    await H.add_word(lid, "property", "xossa", "свойство", source="ai", order=1)
    r = await async_client.get(_url(cid, lid), headers=H.h(sid))
    assert r.status_code == 200, r.text
    assert [(w["word"], w["definition_ru"], w["source"]) for w in r.json()] == [
        ("selector", None, "manual"), ("property", "свойство", "ai")]


async def test_put_vocab_updates_definition_ru_and_keeps_it_when_omitted(async_client):
    tid = await H.make_user(teacher=True)
    cid, (lid,) = await H.make_course(tid)
    vid = await H.add_word(lid, "selector", "tanlagich", "старое")
    r = await async_client.put(_url(cid, lid, f"/{vid}"), headers=H.h(tid),
                               json={"word": "selector", "definition": "tanlagich", "definition_ru": "селектор"})
    assert r.status_code == 200 and r.json()["definition_ru"] == "селектор"
    r = await async_client.put(_url(cid, lid, f"/{vid}"), headers=H.h(tid),
                               json={"word": "selector", "definition": "yangi"})
    assert r.json()["definition"] == "yangi" and r.json()["definition_ru"] == "селектор"
