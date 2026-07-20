"""Seed the initial Phase-1 store catalogue.

Upserts a handful of cosmetic items — themes, fonts, and submit-sound
packs — by slug. Safe to run repeatedly: existing rows are updated in
place, missing rows are inserted, and no rows are ever deleted (so a
teacher who tweaks a title in the admin UI won't get overwritten on the
next seed run — only fields declared here move).

Usage:
    cd backend
    python scripts/seed_store_catalogue.py            # dry-run
    python scripts/seed_store_catalogue.py --apply    # actually write

The `asset_ref` shape by kind:

    theme:      {"tokens": {"--color-primary": "...", ...}, "mode": "light|dark"}
    font:       {"family": "Fira Code", "css_url": null, "stack": "'Fira Code', monospace"}
    sound_pack: {"submit_ok_url": "/static/sounds/xxx.mp3", "submit_fail_url": "..."}

The frontend reads `asset_ref` verbatim and applies it via a CSS-var
switch (themes/fonts) or by playing the URL (sounds).
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.db.database import AsyncSessionLocal, engine
from app.db import base as _base  # noqa: F401
from app.models.store import StoreItem, StoreItemKind


CATALOGUE: list[dict] = [
    # ─── themes ──────────────────────────────────────────────────────
    {
        "slug": "theme.neon",
        "kind": StoreItemKind.theme,
        "title": "Neon Pulse",
        "title_ru": "Неоновый пульс",
        "description": "Elektr binafshalar va pushti fluor — kechqurun kod yozish uchun.",
        "description_ru": "Электрические фиолетовые и розовый флуор — для работы вечером.",
        "price_coins": 500,
        "sort_order": 10,
        "asset_ref": {
            "mode": "dark",
            "tokens": {
                "--color-primary": "#b967ff",
                "--color-primary-mid": "#c987ff",
                "--color-primary-light": "#e0b5ff",
                "--color-primary-pale": "rgba(185, 103, 255, 0.14)",
                "--color-ink": "#f5f1ff",
                "--color-dark": "#0a0716",
                "--bg-page": "#120b23",
                "--text-strong": "rgba(245, 241, 255, 0.94)",
                "--text-muted": "rgba(245, 241, 255, 0.66)",
                "--shadow-brand": "0 4px 24px rgba(185, 103, 255, 0.35)",
            },
        },
    },
    {
        "slug": "theme.cyberpunk",
        "kind": StoreItemKind.theme,
        "title": "Cyberpunk 2077",
        "title_ru": "Киберпанк 2077",
        "description": "Sariq va moviy — futuristik shahar kabi.",
        "description_ru": "Жёлтый и голубой — как футуристический город.",
        "price_coins": 500,
        "sort_order": 20,
        "asset_ref": {
            "mode": "dark",
            "tokens": {
                "--color-primary": "#ffcc00",
                "--color-primary-mid": "#ffd633",
                "--color-primary-light": "#ffe066",
                "--color-primary-pale": "rgba(255, 204, 0, 0.12)",
                "--color-ink": "#e8faff",
                "--color-dark": "#050912",
                "--bg-page": "#0a1420",
                "--text-strong": "rgba(232, 250, 255, 0.95)",
                "--text-muted": "rgba(232, 250, 255, 0.65)",
                "--shadow-brand": "0 4px 24px rgba(255, 204, 0, 0.30)",
            },
        },
    },
    {
        "slug": "theme.hacker",
        "kind": StoreItemKind.theme,
        "title": "Green Terminal",
        "title_ru": "Зелёный терминал",
        "description": "Klassik hacker terminal — qora ekran, yashil harflar.",
        "description_ru": "Классический хакерский терминал — чёрный экран, зелёные буквы.",
        "price_coins": 400,
        "sort_order": 30,
        "asset_ref": {
            "mode": "dark",
            "tokens": {
                "--color-primary": "#00ff88",
                "--color-primary-mid": "#33ff9c",
                "--color-primary-light": "#66ffb0",
                "--color-primary-pale": "rgba(0, 255, 136, 0.10)",
                "--color-ink": "#d1ffe0",
                "--color-dark": "#020604",
                "--bg-page": "#050d08",
                "--text-strong": "rgba(209, 255, 224, 0.95)",
                "--text-muted": "rgba(209, 255, 224, 0.60)",
                "--shadow-brand": "0 4px 24px rgba(0, 255, 136, 0.25)",
            },
        },
    },
    {
        "slug": "theme.sunset",
        "kind": StoreItemKind.theme,
        "title": "Sunset Coral",
        "title_ru": "Закат — коралл",
        "description": "Iliq to'q sariq va shaftoli — kunning oxiri uchun.",
        "description_ru": "Тёплый оранжевый и персиковый — для конца дня.",
        "price_coins": 400,
        "sort_order": 40,
        "asset_ref": {
            "mode": "light",
            "tokens": {
                "--color-primary": "#ff6b6b",
                "--color-primary-mid": "#ff8a80",
                "--color-primary-light": "#ffb3a6",
                "--color-primary-pale": "rgba(255, 107, 107, 0.10)",
                "--color-ink": "#3d1f1a",
                "--color-dark": "#2b1310",
                "--bg-page": "#fff5f2",
                "--text-strong": "rgba(61, 31, 26, 0.92)",
                "--text-muted": "rgba(61, 31, 26, 0.62)",
                "--shadow-brand": "0 4px 24px rgba(255, 107, 107, 0.18)",
            },
        },
    },

    # ─── fonts ───────────────────────────────────────────────────────
    {
        "slug": "font.jetbrains-mono",
        "kind": StoreItemKind.font,
        "title": "JetBrains Mono",
        "title_ru": "JetBrains Mono",
        "description": "Dasturchilar uchun mo'ljallangan mono-shrift — ligaturalari bilan.",
        "description_ru": "Моношрифт для разработчиков — с лигатурами.",
        "price_coins": 250,
        "sort_order": 100,
        "asset_ref": {
            "family": "JetBrains Mono",
            "stack": "'JetBrains Mono', 'Fira Code', ui-monospace, monospace",
            "target": "mono",
        },
    },
    {
        "slug": "font.space-grotesk",
        "kind": StoreItemKind.font,
        "title": "Space Grotesk",
        "title_ru": "Space Grotesk",
        "description": "Zamonaviy geometrik shrift — sarlavhalar uchun.",
        "description_ru": "Современный геометрический шрифт — для заголовков.",
        "price_coins": 250,
        "sort_order": 110,
        "asset_ref": {
            "family": "Space Grotesk",
            "stack": "'Space Grotesk', 'Inter', 'Segoe UI', system-ui, sans-serif",
            "target": "ui",
        },
    },

    # ─── sound packs ─────────────────────────────────────────────────
    {
        "slug": "sound.arcade",
        "kind": StoreItemKind.sound_pack,
        "title": "Arcade — 8-bit",
        "title_ru": "Arcade — 8-bit",
        "description": "Retro o'yin ovozlari — mashqni to'g'ri bajarganda.",
        "description_ru": "Ретро игровые звуки — при правильном ответе.",
        "price_coins": 150,
        "sort_order": 200,
        "asset_ref": {
            "submit_ok_url": "/static/sounds/arcade_ok.mp3",
            "submit_fail_url": "/static/sounds/arcade_fail.mp3",
            "celebration_url": "/static/sounds/arcade_win.mp3",
        },
    },
    {
        "slug": "sound.applause",
        "kind": StoreItemKind.sound_pack,
        "title": "Applause",
        "title_ru": "Аплодисменты",
        "description": "Har bir bajarilgan mashq — kichik ovoz karnavali.",
        "description_ru": "Каждое выполненное задание — маленький карнавал звуков.",
        "price_coins": 150,
        "sort_order": 210,
        "asset_ref": {
            "submit_ok_url": "/static/sounds/applause_ok.mp3",
            "submit_fail_url": "/static/sounds/applause_fail.mp3",
            "celebration_url": "/static/sounds/applause_win.mp3",
        },
    },
]


UPSERT_FIELDS = (
    "kind", "title", "title_ru", "description", "description_ru",
    "price_coins", "asset_ref", "sort_order",
)


async def seed(apply: bool) -> None:
    label = "APPLY" if apply else "DRY-RUN"
    print(f"=== Seed store catalogue ({label}) ===")
    inserted = updated = unchanged = 0

    async with AsyncSessionLocal() as db:
        for entry in CATALOGUE:
            existing = (
                await db.execute(select(StoreItem).where(StoreItem.slug == entry["slug"]))
            ).scalar_one_or_none()

            if existing is None:
                inserted += 1
                print(f"  + insert  {entry['slug']:<28} {entry['price_coins']:>5} coins")
                if apply:
                    db.add(StoreItem(is_active=True, **entry))
                continue

            changes: list[str] = []
            for field in UPSERT_FIELDS:
                new_value = entry.get(field)
                old_value = getattr(existing, field)
                # Compare enum-vs-enum properly.
                if hasattr(old_value, "value"):
                    old_value = old_value.value
                if hasattr(new_value, "value"):
                    new_value = new_value.value
                if old_value != new_value:
                    changes.append(field)
                    if apply:
                        setattr(existing, field, entry[field])

            if changes:
                updated += 1
                print(f"  ~ update  {entry['slug']:<28} → {', '.join(changes)}")
            else:
                unchanged += 1

        if apply:
            await db.commit()

    print(f"\n--- Summary: {inserted} inserted / {updated} updated / {unchanged} unchanged ---")
    if not apply:
        print("(dry-run — no changes written. Re-run with --apply to commit.)")

    await engine.dispose()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--apply", action="store_true", help="Actually write to the DB.")
    args = p.parse_args()
    asyncio.run(seed(apply=args.apply))


if __name__ == "__main__":
    main()
