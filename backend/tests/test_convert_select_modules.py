"""scripts/convert_select_modules.py: mixes all-select modules into active games, reversibly.

Every test limits the script to its own modules (load_modules is wrapped):
the shared test database holds other tests' all-select modules too.
"""
import json
import uuid

import pytest
from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.models.early_learning import EarlyActivity, EarlyModule
from scripts import convert_select_modules as conv
from tests._early_helpers import make_module, make_teacher

PLAN = ["select", "collect", "connect", "catch", "dragsort",
        "collect", "connect", "catch", "dragsort", "select"]


def _limit_to(monkeypatch, module_ids):
    real = conv.load_modules

    async def only_mine(db):
        return [pair for pair in await real(db) if pair[0].id in module_ids]

    monkeypatch.setattr(conv, "load_modules", only_mine)


def _content(tag, mod, k, mode="select"):
    return {
        "mode": mode,
        "character": {"label": f"Qahramon {tag}-{mod}-{k}", "label_ru": f"Герой {tag}-{mod}-{k}", "emoji": "🙂"},
        "correct_items": [
            {"label": f"Narsa {mod}-{k}-{j}", "label_ru": f"Вещь {mod}-{k}-{j}", "emoji": "🍎"} for j in range(4)
        ],
        "distractor_items": [{"label": f"Chalg'ituvchi {mod}-{k}", "label_ru": f"Лишнее {mod}-{k}", "emoji": "🔨"}],
    }


async def _modules(async_client, db_session, count=3, n=10, mixed=False, base_order=900000):
    """`count` all-select modules (display_order ascending) of n games each,
    plus (mixed=True) one module with a maze among its games."""
    tag = uuid.uuid4().hex[:6]
    teacher = await make_teacher(async_client, db_session)
    out = []
    specs = [("select",) * n] * count + ([("select", "maze", "select")] if mixed else [])
    for m, modes in enumerate(specs):
        module, acts = await make_module(db_session, teacher, n_activities=len(modes), modes=list(modes))
        module.display_order = base_order + m
        for k, (a, mode) in enumerate(zip(acts, modes)):
            a.content_json = json.dumps(_content(tag, m, k, mode), ensure_ascii=False)
            a.instruction_text = f"Asl matn {tag} {m} {k}"
            a.instruction_text_ru = f"Исходный текст {tag} {m} {k}" if k % 2 == 0 else None
        out.append(module)
    await db_session.commit()
    return [mod.id for mod in out]


async def _state(module_id):
    async with AsyncSessionLocal() as db:
        rows = (await db.execute(
            select(EarlyActivity).where(EarlyActivity.module_id == module_id).order_by(EarlyActivity.order)
        )).scalars().all()
        return [(a.content_json, a.instruction_text, a.instruction_text_ru) for a in rows]


def _modes(state):
    return [json.loads(c).get("mode") for c, _, _ in state]


def test_mode_for_plan():
    assert [conv.mode_for(i, 10) for i in range(10)] == PLAN
    assert [conv.mode_for(i, 7) for i in range(7)] == PLAN[:6] + ["select"]
    twelve = [conv.mode_for(i, 12) for i in range(12)]
    assert twelve[:11] == PLAN + PLAN[:1] and twelve[-1] == "select"
    assert conv.mode_for(0, 1) == "select"


async def test_converts_full_select_modules_in_order(async_client, db_session, monkeypatch):
    ids = await _modules(async_client, db_session, count=3, mixed=True)
    _limit_to(monkeypatch, set(ids))
    mixed_before = await _state(ids[3])
    out = await conv.run(dry_run=False, module_id=None, revert=False)
    for mid in ids[:3]:
        assert _modes(await _state(mid)) == PLAN
    assert await _state(ids[3]) == mixed_before
    assert out["changed"] == 3 * 8
    assert [m["id"] for m in out["modules"]] == ids[:3]


async def test_partner_comes_from_next_module(async_client, db_session, monkeypatch):
    ids = await _modules(async_client, db_session, count=3)
    _limit_to(monkeypatch, set(ids))
    originals = [[json.loads(c) for c, _, _ in await _state(mid)] for mid in ids]
    await conv.run(dry_run=False, module_id=None, revert=False)
    m0 = [json.loads(c) for c, _, _ in await _state(ids[0])]
    m2 = [json.loads(c) for c, _, _ in await _state(ids[2])]
    k = 4  # the 5th game is a dragsort
    assert m0[k]["mode"] == "dragsort"
    assert m0[k]["partner"] == {"character": originals[1][k]["character"],
                                "correct_items": originals[1][k]["correct_items"]}
    assert m0[k]["partner2"]["character"] == originals[2][k]["character"]
    assert m0[k]["partner"]["character"]["label_ru"].startswith("Герой")
    # M2 wraps around: partner from M0, partner2 from M1.
    assert m2[k]["partner"]["character"] == originals[0][k]["character"]
    assert m2[k]["partner2"]["character"] == originals[1][k]["character"]
    # Only dragsort games get partners.
    assert "partner" not in m0[1] and "partner" not in m0[0]


async def test_instructions_follow_template(async_client, db_session, monkeypatch):
    ids = await _modules(async_client, db_session, count=3)
    _limit_to(monkeypatch, set(ids))
    before = await _state(ids[0])
    await conv.run(dry_run=False, module_id=None, revert=False)
    after = await _state(ids[0])
    content = [json.loads(c) for c, _, _ in before]
    x, x_ru = content[1]["character"]["label"], content[1]["character"]["label_ru"]
    assert after[1][1] == f"Labirintda yurib, {x} uchun kerakli narsalarni yig'."
    assert after[1][2] == f"Пройди лабиринт и собери то, что нужно для: {x_ru}."
    y, y_ru = content[2]["character"]["label"], content[2]["character"]["label_ru"]
    assert after[2][1] == f"{y} ga mos narsalarni chiziq bilan ula."
    assert after[2][2] == f"Соедини линией подходящие предметы с: {y_ru}."
    z, z_ru = content[3]["character"]["label"], content[3]["character"]["label_ru"]
    assert after[3][1] == f"{z} ga mos narsalarni savatga tut."
    assert after[3][2] == f"Лови в корзину то, что подходит для: {z_ru}."
    assert after[4][1] == "Narsalarni to'g'ri savatga sudrab joyla."
    assert after[4][2] == "Перетащи предметы в нужные корзины."
    # select games keep their text and content.
    assert after[0] == before[0] and after[9] == before[9]
    conv_from = json.loads(after[1][0])["converted_from"]
    assert conv_from == {"mode": "select", "instruction_text": before[1][1], "instruction_text_ru": before[1][2]}


def test_instruction_ru_falls_back_to_uz_label():
    assert conv.instruction_for("catch", {"label": "Oshpaz"}, "ru") == "Лови в корзину то, что подходит для: Oshpaz."
    assert conv.instruction_for("select", {"label": "Oshpaz"}, "uz") is None


async def test_dry_run_writes_nothing(async_client, db_session, monkeypatch):
    ids = await _modules(async_client, db_session, count=3)
    _limit_to(monkeypatch, set(ids))
    before = [await _state(mid) for mid in ids]
    out = await conv.run(dry_run=True, module_id=None, revert=False)
    assert [await _state(mid) for mid in ids] == before
    assert out["changed"] == 24
    assert out["modules"][0]["modes"] == PLAN


async def test_second_run_changes_nothing(async_client, db_session, monkeypatch):
    ids = await _modules(async_client, db_session, count=3)
    _limit_to(monkeypatch, set(ids))
    await conv.run(dry_run=False, module_id=None, revert=False)
    after_first = [await _state(mid) for mid in ids]
    out = await conv.run(dry_run=False, module_id=None, revert=False)
    assert out["changed"] == 0
    assert [await _state(mid) for mid in ids] == after_first


async def test_revert_restores_exactly(async_client, db_session, monkeypatch):
    ids = await _modules(async_client, db_session, count=3)
    _limit_to(monkeypatch, set(ids))
    before = [await _state(mid) for mid in ids]
    await conv.run(dry_run=False, module_id=None, revert=False)
    out = await conv.run(dry_run=False, module_id=None, revert=True)
    assert out["changed"] == 24
    after = [await _state(mid) for mid in ids]
    assert after == before  # byte for byte: content_json strings and both texts
    for state in after:
        for c, _, _ in state:
            assert "converted_from" not in json.loads(c)


async def test_revert_restores_a_missing_mode(async_client, db_session, monkeypatch):
    ids = await _modules(async_client, db_session, count=2, n=3)
    async with AsyncSessionLocal() as db:
        acts = (await db.execute(select(EarlyActivity).where(EarlyActivity.module_id == ids[0]))).scalars().all()
        for a in acts:
            c = json.loads(a.content_json)
            c.pop("mode")
            a.content_json = json.dumps(c, ensure_ascii=False)
        await db.commit()
    _limit_to(monkeypatch, set(ids))
    before = await _state(ids[0])
    await conv.run(dry_run=False, module_id=None, revert=False)
    assert _modes(await _state(ids[0])) == [None, "collect", None]
    await conv.run(dry_run=False, module_id=None, revert=True)
    assert await _state(ids[0]) == before


async def test_single_module_partner_from_other_select_modules(async_client, db_session, monkeypatch):
    ids = await _modules(async_client, db_session, count=3)
    _limit_to(monkeypatch, set(ids))
    originals = [[json.loads(c) for c, _, _ in await _state(mid)] for mid in ids]
    others = [await _state(mid) for mid in ids[1:]]
    out = await conv.run(dry_run=False, module_id=ids[1], revert=False)
    assert [m["id"] for m in out["modules"]] == [ids[1]]
    m1 = [json.loads(c) for c, _, _ in await _state(ids[1])]
    assert _modes(await _state(ids[1])) == PLAN
    assert m1[4]["partner"]["character"] == originals[2][4]["character"]
    assert m1[4]["partner2"]["character"] == originals[0][4]["character"]
    assert [await _state(mid) for mid in ids[2:]] == others[1:]
    assert _modes(await _state(ids[0])) == ["select"] * 10


async def test_lone_module_gets_no_partner_from_itself(async_client, db_session, monkeypatch):
    ids = await _modules(async_client, db_session, count=1)
    _limit_to(monkeypatch, set(ids))
    await conv.run(dry_run=False, module_id=None, revert=False)
    m0 = [json.loads(c) for c, _, _ in await _state(ids[0])]
    assert m0[4]["mode"] == "dragsort"
    assert "partner" not in m0[4] and "partner2" not in m0[4]


async def test_inactive_module_is_not_touched(async_client, db_session, monkeypatch):
    ids = await _modules(async_client, db_session, count=2)
    async with AsyncSessionLocal() as db:
        mod = await db.get(EarlyModule, ids[1])
        mod.is_active = False
        await db.commit()
    _limit_to(monkeypatch, set(ids))
    before = await _state(ids[1])
    await conv.run(dry_run=False, module_id=None, revert=False)
    assert await _state(ids[1]) == before
    assert _modes(await _state(ids[0])) == PLAN


def test_main_dry_run_prints_and_reminds(monkeypatch, capsys):
    async def fake_run(**kw):
        assert kw == {"dry_run": True, "module_id": 7, "revert": False}
        return {"modules": [{"id": 7, "title": "Kasblar", "modes": ["select", "collect"], "partners": []}],
                "changed": 1, "skipped": 1}

    monkeypatch.setattr(conv, "run", fake_run)
    conv.main(["--dry-run", "--module", "7"])
    printed = capsys.readouterr().out
    assert "Kasblar" in printed and "collect" in printed


async def test_modeless_draft_modules_are_neither_converted_nor_partners(async_client, db_session, monkeypatch):
    """The seed's draft modules have no `mode` and no select content
    ({"targets": ...}, {"pairs": ...}): they are not select games."""
    ids = await _modules(async_client, db_session, count=3, base_order=800000)
    teacher = await make_teacher(async_client, db_session)
    draft, acts = await make_module(db_session, teacher, n_activities=10)
    draft.display_order = 800010  # right after the select modules: would be M3 of the ring
    for a in acts:
        a.content_json = json.dumps({"targets": [{"id": "a", "label": "A"}]}, ensure_ascii=False)
    await db_session.commit()
    _limit_to(monkeypatch, set(ids) | {draft.id})
    before = await _state(draft.id)
    out = await conv.run(dry_run=False, module_id=None, revert=False)
    assert draft.id not in [m["id"] for m in out["modules"]]
    assert await _state(draft.id) == before
    # The last select module wraps around to the first select module, not to the draft.
    last = [json.loads(c) for c, _, _ in await _state(ids[2])]
    first = [json.loads(c) for c, _, _ in await _state(ids[0])]
    assert last[4]["partner"]["character"] == first[4]["character"]
    assert "partner2" in last[4]
