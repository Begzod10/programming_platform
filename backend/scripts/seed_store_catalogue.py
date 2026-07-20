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
    {
        "slug": "theme.nord",
        "kind": StoreItemKind.theme,
        "title": "Nord — Arctic Blue",
        "title_ru": "Nord — арктический синий",
        "description": "Sovuq shimoliy palitra — dasturchilar sevgan Nord teması.",
        "description_ru": "Холодная северная палитра — любимая тема разработчиков Nord.",
        "price_coins": 550,
        "sort_order": 50,
        "asset_ref": {
            "mode": "dark",
            "tokens": {
                "--color-primary": "#88c0d0",
                "--color-primary-mid": "#8fbcbb",
                "--color-primary-light": "#a3be8c",
                "--color-primary-pale": "rgba(136, 192, 208, 0.12)",
                "--color-ink": "#eceff4",
                "--color-dark": "#2e3440",
                "--bg-page": "#3b4252",
                "--text-strong": "rgba(236, 239, 244, 0.94)",
                "--text-muted": "rgba(216, 222, 233, 0.68)",
                "--shadow-brand": "0 4px 24px rgba(136, 192, 208, 0.24)",
            },
        },
    },
    {
        "slug": "theme.vaporwave",
        "kind": StoreItemKind.theme,
        "title": "Vaporwave 90s",
        "title_ru": "Vaporwave — 90-е",
        "description": "Pushti va tsian — nostalgiya bilan to'la retro estetika.",
        "description_ru": "Розовый и циан — ретро-эстетика, полная ностальгии.",
        "price_coins": 600,
        "sort_order": 60,
        "asset_ref": {
            "mode": "dark",
            "tokens": {
                "--color-primary": "#ff71ce",
                "--color-primary-mid": "#ff85d5",
                "--color-primary-light": "#01cdfe",
                "--color-primary-pale": "rgba(255, 113, 206, 0.14)",
                "--color-ink": "#fff8fd",
                "--color-dark": "#1a0a2e",
                "--bg-page": "#2a1447",
                "--text-strong": "rgba(255, 248, 253, 0.94)",
                "--text-muted": "rgba(255, 240, 250, 0.66)",
                "--shadow-brand": "0 4px 24px rgba(255, 113, 206, 0.30)",
            },
        },
    },
    {
        "slug": "theme.sakura",
        "kind": StoreItemKind.theme,
        "title": "Sakura Bloom",
        "title_ru": "Цветение сакуры",
        "description": "Nozik pushti va bahor palitrasi — engil, iliq va toza.",
        "description_ru": "Нежно-розовая весенняя палитра — лёгкая, тёплая и чистая.",
        "price_coins": 450,
        "sort_order": 70,
        "asset_ref": {
            "mode": "light",
            "tokens": {
                "--color-primary": "#e91e63",
                "--color-primary-mid": "#ec407a",
                "--color-primary-light": "#f8bbd0",
                "--color-primary-pale": "rgba(233, 30, 99, 0.08)",
                "--color-ink": "#3a1e2e",
                "--color-dark": "#28131f",
                "--bg-page": "#fff0f5",
                "--text-strong": "rgba(58, 30, 46, 0.92)",
                "--text-muted": "rgba(58, 30, 46, 0.60)",
                "--shadow-brand": "0 4px 24px rgba(233, 30, 99, 0.18)",
            },
        },
    },
    {
        "slug": "theme.ocean",
        "kind": StoreItemKind.theme,
        "title": "Ocean Depths",
        "title_ru": "Океанские глубины",
        "description": "Chuqur firuza va navy — dengiz osti dunyosining tinchligi.",
        "description_ru": "Глубокая бирюза и navy — спокойствие подводного мира.",
        "price_coins": 500,
        "sort_order": 80,
        "asset_ref": {
            "mode": "dark",
            "tokens": {
                "--color-primary": "#26c6da",
                "--color-primary-mid": "#4dd0e1",
                "--color-primary-light": "#80deea",
                "--color-primary-pale": "rgba(38, 198, 218, 0.10)",
                "--color-ink": "#e0f7fa",
                "--color-dark": "#001f2b",
                "--bg-page": "#00343f",
                "--text-strong": "rgba(224, 247, 250, 0.95)",
                "--text-muted": "rgba(178, 223, 238, 0.62)",
                "--shadow-brand": "0 4px 24px rgba(38, 198, 218, 0.28)",
            },
        },
    },
    {
        "slug": "theme.solarized",
        "kind": StoreItemKind.theme,
        "title": "Solarized Dark",
        "title_ru": "Solarized Dark",
        "description": "Ilmiy-tekshirilgan kontrast, ko'zga engil — Solarized klassikasi.",
        "description_ru": "Научно выверенный контраст, легко воспринимается — классика Solarized.",
        "price_coins": 550,
        "sort_order": 90,
        "asset_ref": {
            "mode": "dark",
            "tokens": {
                "--color-primary": "#268bd2",
                "--color-primary-mid": "#2aa198",
                "--color-primary-light": "#b58900",
                "--color-primary-pale": "rgba(38, 139, 210, 0.10)",
                "--color-ink": "#eee8d5",
                "--color-dark": "#002b36",
                "--bg-page": "#073642",
                "--text-strong": "rgba(238, 232, 213, 0.95)",
                "--text-muted": "rgba(147, 161, 161, 0.85)",
                "--shadow-brand": "0 4px 24px rgba(38, 139, 210, 0.22)",
            },
        },
    },
    {
        "slug": "theme.autumn",
        "kind": StoreItemKind.theme,
        "title": "Autumn Forest",
        "title_ru": "Осенний лес",
        "description": "Yong'oq, kashtan va o'rmon — kuz oxiri palitrasi.",
        "description_ru": "Каштан, орех и лесная зелень — палитра позднего листопада.",
        "price_coins": 450,
        "sort_order": 100,
        "asset_ref": {
            "mode": "light",
            "tokens": {
                "--color-primary": "#a0522d",
                "--color-primary-mid": "#c67958",
                "--color-primary-light": "#e8b696",
                "--color-primary-pale": "rgba(160, 82, 45, 0.08)",
                "--color-ink": "#2c1810",
                "--color-dark": "#1a0e08",
                "--bg-page": "#faf3ea",
                "--text-strong": "rgba(44, 24, 16, 0.92)",
                "--text-muted": "rgba(44, 24, 16, 0.60)",
                "--shadow-brand": "0 4px 24px rgba(160, 82, 45, 0.18)",
            },
        },
    },
    {
        "slug": "theme.amethyst",
        "kind": StoreItemKind.theme,
        "title": "Midnight Amethyst",
        "title_ru": "Полуночный аметист",
        "description": "Chuqur binafsha va oltinsimon aksent — sirli va nafis.",
        "description_ru": "Глубокий фиолетовый с золотистым акцентом — таинственно и изысканно.",
        "price_coins": 700,
        "sort_order": 110,
        "asset_ref": {
            "mode": "dark",
            "tokens": {
                "--color-primary": "#9575cd",
                "--color-primary-mid": "#b39ddb",
                "--color-primary-light": "#ffd54f",
                "--color-primary-pale": "rgba(149, 117, 205, 0.12)",
                "--color-ink": "#ede7f6",
                "--color-dark": "#170e2e",
                "--bg-page": "#231650",
                "--text-strong": "rgba(237, 231, 246, 0.95)",
                "--text-muted": "rgba(209, 196, 233, 0.68)",
                "--shadow-brand": "0 4px 24px rgba(149, 117, 205, 0.30)",
            },
        },
    },
    {
        "slug": "theme.mint",
        "kind": StoreItemKind.theme,
        "title": "Fresh Mint",
        "title_ru": "Свежая мята",
        "description": "Ochiq yashil va toza oq — bahor kabi ochiq.",
        "description_ru": "Светло-зелёный и чистый белый — открыто, как весна.",
        "price_coins": 400,
        "sort_order": 120,
        "asset_ref": {
            "mode": "light",
            "tokens": {
                "--color-primary": "#00c896",
                "--color-primary-mid": "#26d9ac",
                "--color-primary-light": "#66e5c8",
                "--color-primary-pale": "rgba(0, 200, 150, 0.08)",
                "--color-ink": "#0f2e26",
                "--color-dark": "#062018",
                "--bg-page": "#f0fbf7",
                "--text-strong": "rgba(15, 46, 38, 0.92)",
                "--text-muted": "rgba(15, 46, 38, 0.58)",
                "--shadow-brand": "0 4px 24px rgba(0, 200, 150, 0.20)",
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
    {
        "slug": "font.fira-code",
        "kind": StoreItemKind.font,
        "title": "Fira Code",
        "title_ru": "Fira Code",
        "description": "Mozilla-ning mashhur ligaturali kod shrifti.",
        "description_ru": "Знаменитый моношрифт от Mozilla с лигатурами.",
        "price_coins": 250,
        "sort_order": 120,
        "asset_ref": {
            "family": "Fira Code",
            "stack": "'Fira Code', 'JetBrains Mono', ui-monospace, monospace",
            "target": "mono",
        },
    },
    {
        "slug": "font.cascadia-code",
        "kind": StoreItemKind.font,
        "title": "Cascadia Code",
        "title_ru": "Cascadia Code",
        "description": "Microsoft'ning zamonaviy kod shrifti — Windows Terminal uchun.",
        "description_ru": "Современный моношрифт Microsoft — для Windows Terminal.",
        "price_coins": 250,
        "sort_order": 130,
        "asset_ref": {
            "family": "Cascadia Code",
            "stack": "'Cascadia Code', 'Cascadia Mono', 'JetBrains Mono', ui-monospace, monospace",
            "target": "mono",
        },
    },
    {
        "slug": "font.playfair",
        "kind": StoreItemKind.font,
        "title": "Playfair Display",
        "title_ru": "Playfair Display",
        "description": "Klassik serif — sarlavhalar uchun nafis va zamonaviy.",
        "description_ru": "Классический серифный шрифт — элегантно и современно для заголовков.",
        "price_coins": 350,
        "sort_order": 140,
        "asset_ref": {
            "family": "Playfair Display",
            "stack": "'Playfair Display', 'Georgia', 'Times New Roman', serif",
            "target": "ui",
        },
    },
    {
        "slug": "font.poppins",
        "kind": StoreItemKind.font,
        "title": "Poppins",
        "title_ru": "Poppins",
        "description": "Yumshoq geometrik sans — do'stona va o'qishga oson.",
        "description_ru": "Мягкий геометрический sans — дружелюбный и легко читаемый.",
        "price_coins": 300,
        "sort_order": 150,
        "asset_ref": {
            "family": "Poppins",
            "stack": "'Poppins', 'Segoe UI', system-ui, sans-serif",
            "target": "ui",
        },
    },
    {
        "slug": "font.ibm-plex-mono",
        "kind": StoreItemKind.font,
        "title": "IBM Plex Mono",
        "title_ru": "IBM Plex Mono",
        "description": "IBM'ning mashhur kod shrifti — professional va toza.",
        "description_ru": "Знаменитый моношрифт IBM — профессиональный и чистый.",
        "price_coins": 300,
        "sort_order": 160,
        "asset_ref": {
            "family": "IBM Plex Mono",
            "stack": "'IBM Plex Mono', 'JetBrains Mono', ui-monospace, monospace",
            "target": "mono",
        },
    },

    # ─── sound packs ─────────────────────────────────────────────────
    # Sound packs currently ship as Web-Audio synth presets — no binary
    # assets to serve. The frontend's playSoundAsset() falls back to the
    # `synth` name when no `submit_ok_url` is present, so we can later
    # swap in real .mp3 files by adding those keys without a schema
    # change.
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
            "synth": "arcade",
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
            "synth": "applause",
        },
    },
    {
        "slug": "sound.coin",
        "kind": StoreItemKind.sound_pack,
        "title": "Coin Drop",
        "title_ru": "Звон монеты",
        "description": "Klassik Mario tanga tovushi — har xato javob ham quvonchli.",
        "description_ru": "Классический звон монеты Марио — даже ошибка приятная.",
        "price_coins": 150,
        "sort_order": 220,
        "asset_ref": {
            "synth": "coin",
        },
    },
    {
        "slug": "sound.laser",
        "kind": StoreItemKind.sound_pack,
        "title": "Laser Zap",
        "title_ru": "Лазерный залп",
        "description": "Ilm-fantastika ovozlari — kod yozganda kosmik his qiling.",
        "description_ru": "Sci-fi звуки — почувствуйте себя в космосе, пока пишете код.",
        "price_coins": 200,
        "sort_order": 230,
        "asset_ref": {
            "synth": "laser",
        },
    },
    {
        "slug": "sound.chime",
        "kind": StoreItemKind.sound_pack,
        "title": "Zen Chime",
        "title_ru": "Дзен-колокольчик",
        "description": "Yumshoq qo'ng'iroq arpeggiosi — tinch va konsentratsiya uchun.",
        "description_ru": "Мягкое арпеджио колокольчика — тихо и для концентрации.",
        "price_coins": 175,
        "sort_order": 240,
        "asset_ref": {
            "synth": "chime",
        },
    },
    {
        "slug": "sound.fanfare",
        "kind": StoreItemKind.sound_pack,
        "title": "Royal Fanfare",
        "title_ru": "Королевские фанфары",
        "description": "Karnaylar sadosi — g'olibga munosib salomlashuv.",
        "description_ru": "Трубы во славу — приветствие, достойное победителя.",
        "price_coins": 300,
        "sort_order": 250,
        "asset_ref": {
            "synth": "fanfare",
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
