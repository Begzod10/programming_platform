"""Turn the kids' modules whose games are all "select" into a mix of active games (collect, connect, catch, dragsort).

Only content_json (mode, dragsort partner/partner2) and the instruction texts change. The original mode and
texts are kept in content_json["converted_from"], so --revert puts every game back exactly as it was.

    python scripts/convert_select_modules.py --dry-run           # what would change; writes nothing
    python scripts/convert_select_modules.py                     # convert every all-select module
    python scripts/convert_select_modules.py --module 12         # only module 12 (partners from the other select modules)
    python scripts/convert_select_modules.py --revert            # undo (all, or with --module just one)

One transaction. Afterwards run scripts/generate_early_audio.py for the new instruction voices.

See docs/superpowers/specs/2026-11-16-early-active-games-design.md §3.3–3.5.
"""
from __future__ import annotations

import argparse
import asyncio
import copy
import json
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select  # noqa: E402

from app.db import base as _all_models  # noqa: E402,F401
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.models.early_learning import EarlyActivity, EarlyModule  # noqa: E402

PLAN = ("select", "collect", "connect", "catch", "dragsort",
        "collect", "connect", "catch", "dragsort", "select")

TEMPLATES = {
    "collect": ("Labirintda yurib, {x} uchun kerakli narsalarni yig'.",
                "Пройди лабиринт и собери то, что нужно для: {x}."),
    "connect": ("{x} ga mos narsalarni chiziq bilan ula.",
                "Соедини линией подходящие предметы с: {x}."),
    "catch": ("{x} ga mos narsalarni savatga tut.",
              "Лови в корзину то, что подходит для: {x}."),
    "dragsort": ("Narsalarni to'g'ri savatga sudrab joyla.",
                 "Перетащи предметы в нужные корзины."),
}


def mode_for(index: int, total: int) -> str:
    """Mode of the game at `index` (0-based, by order) in a module of `total` games: the last is always select."""
    return "select" if index == total - 1 else PLAN[index % len(PLAN)]


def instruction_for(mode: str, character: Optional[dict], lang: str) -> Optional[str]:
    """New instruction text, or None (select, or no character name to fill in) = keep the original."""
    if mode not in TEMPLATES:
        return None
    template = TEMPLATES[mode][1 if lang == "ru" else 0]
    if "{x}" not in template:
        return template
    character = character or {}
    name = (character.get("label_ru") if lang == "ru" else None) or character.get("label")
    return template.format(x=name) if name else None


def _content(activity: EarlyActivity) -> dict:
    try:
        content = json.loads(activity.content_json or "{}")
    except ValueError:
        return {}
    return content if isinstance(content, dict) else {}


def _dump(content: dict, like: str) -> str:
    # The seeds write json.dumps(..., ensure_ascii=False); keep whatever style the original used.
    return json.dumps(content, ensure_ascii=not (like or "").isascii())


async def load_modules(db) -> list[tuple[EarlyModule, list[EarlyActivity]]]:
    """Every active module with its active games, by display_order, id (games by order, id)."""
    modules = (await db.execute(
        select(EarlyModule).where(EarlyModule.is_active.is_(True))
        .order_by(EarlyModule.display_order, EarlyModule.id)
    )).scalars().all()
    if not modules:
        return []
    acts = (await db.execute(
        select(EarlyActivity).where(
            EarlyActivity.module_id.in_([m.id for m in modules]),
            EarlyActivity.is_active.is_(True),
        ).order_by(EarlyActivity.order, EarlyActivity.id)
    )).scalars().all()
    by_module: dict[int, list[EarlyActivity]] = {}
    for a in acts:
        by_module.setdefault(a.module_id, []).append(a)
    return [(m, by_module.get(m.id, [])) for m in modules]


def _all_select(activities: list[EarlyActivity]) -> bool:
    if not activities:
        return False
    for a in activities:
        content = _content(a)
        if "converted_from" in content or (content.get("mode") or "select") != "select":
            return False
    return True


def _partner(ring: list[tuple[EarlyModule, list[EarlyActivity]]], i: int, step: int, k: int) -> Optional[dict]:
    """character + correct_items of game k of module ring[i+step] (k mod its size); None if that is module i."""
    j = (i + step) % len(ring)
    if j == i or (step == 2 and j == (i + 1) % len(ring)):
        return None
    games = ring[j][1]
    source = _content(games[k % len(games)])
    if not isinstance(source.get("character"), dict):
        return None
    return {"character": copy.deepcopy(source["character"]),
            "correct_items": copy.deepcopy(source.get("correct_items") or [])}


async def _convert(db, module_id: Optional[int], dry_run: bool) -> dict:
    ring = [pair for pair in await load_modules(db) if _all_select(pair[1])]
    out = {"modules": [], "changed": 0, "skipped": 0}
    for i, (module, games) in enumerate(ring):
        if module_id is not None and module.id != module_id:
            continue
        report = {"id": module.id, "title": module.title, "modes": [], "partners": []}
        new_rows = []
        for k, activity in enumerate(games):
            mode = mode_for(k, len(games))
            report["modes"].append(mode)
            if mode == "select":
                out["skipped"] += 1
                continue
            raw = activity.content_json
            content = _content(activity)
            original_mode = content.get("mode")
            uz = instruction_for(mode, content.get("character"), "uz")
            ru = instruction_for(mode, content.get("character"), "ru")
            content["mode"] = mode
            if mode == "dragsort":
                for key, step in (("partner", 1), ("partner2", 2)):
                    partner = _partner(ring, i, step, k)
                    if partner:
                        content[key] = partner
                        report["partners"].append(f"{k + 1}. {key}: {partner['character'].get('label')}")
            content["converted_from"] = {
                "mode": original_mode,
                "instruction_text": activity.instruction_text,
                "instruction_text_ru": activity.instruction_text_ru,
            }
            new_rows.append((activity, _dump(content, raw),
                             uz if uz is not None else activity.instruction_text,
                             ru if ru is not None else activity.instruction_text_ru))
            out["changed"] += 1
        # Write after reading the whole ring, so partners always copy original content.
        report["_rows"] = new_rows
        out["modules"].append(report)
    for report in out["modules"]:
        rows = report.pop("_rows")
        if dry_run:
            continue
        for activity, content_json, uz, ru in rows:
            activity.content_json = content_json
            activity.instruction_text = uz
            activity.instruction_text_ru = ru
    return out


async def _revert(db, module_id: Optional[int], dry_run: bool) -> dict:
    out = {"modules": [], "changed": 0, "skipped": 0}
    for module, games in await load_modules(db):
        if module_id is not None and module.id != module_id:
            continue
        report = {"id": module.id, "title": module.title, "modes": [], "partners": []}
        touched = False
        for activity in games:
            content = _content(activity)
            original = content.get("converted_from")
            if not isinstance(original, dict):
                report["modes"].append(content.get("mode") or "select")
                continue
            touched = True
            out["changed"] += 1
            if original.get("mode") is None:
                content.pop("mode", None)
            else:
                content["mode"] = original["mode"]
            for key in ("partner", "partner2", "converted_from"):
                content.pop(key, None)
            report["modes"].append(content.get("mode") or "select")
            if not dry_run:
                activity.content_json = _dump(content, activity.content_json)
                activity.instruction_text = original.get("instruction_text")
                activity.instruction_text_ru = original.get("instruction_text_ru")
        if touched:
            out["modules"].append(report)
    return out


async def run(*, dry_run: bool, module_id: Optional[int], revert: bool) -> dict:
    """{"modules": [{"id", "title", "modes", "partners"}], "changed": games changed, "skipped": select games left}."""
    async with AsyncSessionLocal() as db:
        out = await (_revert if revert else _convert)(db, module_id, dry_run)
        if not dry_run:
            await db.commit()
    return out


def main(argv: Optional[list[str]] = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="show what would change; writes nothing")
    ap.add_argument("--module", type=int, default=None, help="only this module id")
    ap.add_argument("--revert", action="store_true", help="put converted games back as they were")
    a = ap.parse_args(argv)
    out = asyncio.run(run(dry_run=a.dry_run, module_id=a.module, revert=a.revert))
    for m in out["modules"]:
        print(f"[{m['id']}] {m['title']}: {m['modes']}", flush=True)
        for p in m["partners"]:
            print(f"    {p}", flush=True)
    verb = "would change" if a.dry_run else ("reverted" if a.revert else "changed")
    print(f"modules: {len(out['modules'])} | games {verb}: {out['changed']} | select kept: {out['skipped']}", flush=True)
    if not a.dry_run and out["changed"]:
        print("Next: run scripts/generate_early_audio.py so the new instructions get their voice.", flush=True)


if __name__ == "__main__":
    main()
