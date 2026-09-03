"""One-off: seed the initial "early learner" (age 4-6) catalog — 4 modules
covering literacy/math/logic/creative, each with a first pass of activities.
See project_student_platform memory / early_learning.py for the model design
rationale (no AI grading, star-based completion instead of points).

Creates the early_modules / early_activities / early_activity_completions
tables directly via Base.metadata.create_all() scoped to just those three,
rather than through `alembic upgrade` — per backend/.gitignore, this repo's
alembic/versions/ is "managed on server, never committed" (migrations are
applied out-of-band against the server DB, not through the git deploy
pipeline), and the local versions/ directory that does exist has a broken
revision graph on top of that. create_all() is additive-only and
checkfirst=True, so it's a no-op against any table that already exists —
safe to re-run.

Idempotent on content: re-running updates existing rows (matched by
module title / activity title+module) instead of duplicating them.

Media URLs are intentionally left as None — no real assets exist yet.
A content author needs to fill instruction_audio_url and the image/audio
fields inside content_json before publishing (is_published stays False
here on purpose).
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.db import base as _base  # noqa: E402,F401  (registers all models for the mapper registry)
from app.db.base_class import Base  # noqa: E402
from app.models.early_learning import (  # noqa: E402
    EarlyModule, EarlyActivity, EarlyActivityCompletion, EarlySubject, EarlyActivityType,
)

INSTRUCTOR_ID = 2  # rimefara_teach / Begzod Jumaniyozov — existing teacher account

MODULES = [
    {
        "title": "Harflar sayohati",
        "description": "Harflarni tanish, tovushlarni ajratish va birinchi so'zlar.",
        "subject": EarlySubject.literacy,
        "icon_emoji": "🔤",
        "color_accent": "#FF6B6B",
        "display_order": 1,
        "activities": [
            {
                "title": "A dan D gacha — chizib yozamiz",
                "activity_type": EarlyActivityType.trace,
                "instruction_text": "Barmog'ing bilan harfni chiz.",
                "content": {"targets": [
                    {"letter": "A", "outline_url": None},
                    {"letter": "B", "outline_url": None},
                    {"letter": "C", "outline_url": None},
                    {"letter": "D", "outline_url": None},
                ]},
            },
            {
                "title": "Tovush va rasm — moslashtir",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Harfni to'g'ri rasmga ulash.",
                "content": {"pairs": [
                    {"left": "B", "right": "Bola", "image_url": None},
                    {"left": "M", "right": "Mushuk", "image_url": None},
                    {"left": "O", "right": "Olma", "image_url": None},
                ]},
            },
            {
                "title": "Ertak tinglaymiz",
                "activity_type": EarlyActivityType.audio_story,
                "instruction_text": None,
                "content": {
                    "text": "Kichkina quyoncha o'rmonda sayr qilib yurardi...",
                    "audio_url": None,
                    "image_url": None,
                },
            },
            {
                "title": "Harfiga qarab ajrat",
                "activity_type": EarlyActivityType.sort,
                "instruction_text": "Rasmlarni boshlang'ich harfiga qarab joylashtir.",
                "content": {
                    "buckets": ["A", "B"],
                    "items": [
                        {"label": "Arik", "bucket": "A", "image_url": None},
                        {"label": "Baliq", "bucket": "B", "image_url": None},
                        {"label": "Bahor", "bucket": "B", "image_url": None},
                        {"label": "Asal", "bucket": "A", "image_url": None},
                    ],
                },
            },
        ],
    },
    {
        "title": "Sonlar dunyosi",
        "description": "Sanash, shakllarni solishtirish va oddiy tartib.",
        "subject": EarlySubject.math,
        "icon_emoji": "🔢",
        "color_accent": "#4D96FF",
        "display_order": 2,
        "activities": [
            {
                "title": "Sanab ko'ramiz",
                "activity_type": EarlyActivityType.count,
                "instruction_text": "Nechta olma borligini sanab, to'g'ri sonni bos.",
                "content": {"object_image_url": None, "count": 4, "options": [3, 4, 5]},
            },
            {
                "title": "Kattami, kichikmi?",
                "activity_type": EarlyActivityType.sort,
                "instruction_text": "Shakllarni kattaligiga qarab joylashtir.",
                "content": {
                    "buckets": ["Kichik", "Katta"],
                    "items": [
                        {"label": "Kichik doira", "bucket": "Kichik", "image_url": None},
                        {"label": "Katta doira", "bucket": "Katta", "image_url": None},
                        {"label": "Kichik kvadrat", "bucket": "Kichik", "image_url": None},
                        {"label": "Katta kvadrat", "bucket": "Katta", "image_url": None},
                    ],
                },
            },
            {
                "title": "Son va miqdorni ulash",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Sonni tegishli miqdordagi rasmga ulang.",
                "content": {"pairs": [
                    {"left": "1", "right": "1 ta olma", "image_url": None},
                    {"left": "2", "right": "2 ta olma", "image_url": None},
                    {"left": "3", "right": "3 ta olma", "image_url": None},
                ]},
            },
            {
                "title": "1 dan 5 gacha tartibla",
                "activity_type": EarlyActivityType.sequence,
                "instruction_text": "Sonlarni to'g'ri tartibda joylashtir.",
                "content": {"correct_order": [1, 2, 3, 4, 5], "shuffled": [3, 1, 5, 2, 4]},
            },
        ],
    },
    {
        "title": "Fikrlash o'yinlari",
        "description": "Ketma-ketlik, naqshlar va yo'l topish.",
        "subject": EarlySubject.logic,
        "icon_emoji": "🧩",
        "color_accent": "#9B5DE5",
        "display_order": 3,
        "activities": [
            {
                "title": "Kunlik tartib",
                "activity_type": EarlyActivityType.sequence,
                "instruction_text": "Kun tartibini to'g'ri ketma-ketlikda joylashtir.",
                "content": {
                    "correct_order": ["Uyg'onish", "Tishlarni yuvish", "Nonushta", "Kiyinish"],
                    "shuffled": ["Kiyinish", "Uyg'onish", "Nonushta", "Tishlarni yuvish"],
                },
            },
            {
                "title": "Yo'lni top",
                "activity_type": EarlyActivityType.maze,
                "instruction_text": "O'qlar yordamida boshidan oxirigacha yo'l top.",
                "content": {"grid_size": [5, 5], "start": [0, 0], "end": [4, 4], "walls": []},
            },
            {
                "title": "Naqshni davom ettir",
                "activity_type": EarlyActivityType.match,
                "instruction_text": "Naqshdagi keyingi rangni top.",
                "content": {"pattern": ["red", "blue", "red", "blue", "?"], "options": ["red", "blue", "green"], "answer": "red"},
            },
        ],
    },
    {
        "title": "Ijodkorlik burchagi",
        "description": "Bo'yash va shakllarni chizish.",
        "subject": EarlySubject.creative,
        "icon_emoji": "🎨",
        "color_accent": "#FFB84D",
        "display_order": 4,
        "activities": [
            {
                "title": "Erkin bo'yash",
                "activity_type": EarlyActivityType.coloring,
                "instruction_text": "Xohlagan rangda bo'ya.",
                "content": {"templates": [
                    {"id": 1, "outline_url": None},
                    {"id": 2, "outline_url": None},
                    {"id": 3, "outline_url": None},
                ]},
            },
            {
                "title": "Shakllarni chizamiz",
                "activity_type": EarlyActivityType.trace,
                "instruction_text": "Shaklni barmog'ing bilan chiz.",
                "content": {"targets": [
                    {"shape": "circle", "outline_url": None},
                    {"shape": "square", "outline_url": None},
                    {"shape": "triangle", "outline_url": None},
                ]},
            },
        ],
    },
]


async def _upsert_module(db, data: dict) -> EarlyModule:
    existing = (
        await db.execute(select(EarlyModule).where(EarlyModule.title == data["title"]))
    ).scalar_one_or_none()
    if existing is None:
        existing = EarlyModule(instructor_id=INSTRUCTOR_ID)
        db.add(existing)
    existing.description = data["description"]
    existing.subject = data["subject"]
    existing.icon_emoji = data["icon_emoji"]
    existing.color_accent = data["color_accent"]
    existing.display_order = data["display_order"]
    existing.title = data["title"]
    await db.flush()  # populate .id for a brand-new row
    return existing


async def _upsert_activity(db, module_id: int, order: int, data: dict) -> None:
    existing = (
        await db.execute(
            select(EarlyActivity).where(
                EarlyActivity.module_id == module_id,
                EarlyActivity.title == data["title"],
            )
        )
    ).scalar_one_or_none()
    if existing is None:
        existing = EarlyActivity(module_id=module_id)
        db.add(existing)
    existing.title = data["title"]
    existing.order = order
    existing.activity_type = data["activity_type"]
    existing.instruction_text = data["instruction_text"]
    existing.content_json = json.dumps(data["content"], ensure_ascii=False)


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all,
            tables=[
                EarlyModule.__table__,
                EarlyActivity.__table__,
                EarlyActivityCompletion.__table__,
            ],
        )

    modules_written = 0
    activities_written = 0
    async with AsyncSessionLocal() as db:
        for mod_data in MODULES:
            module = await _upsert_module(db, mod_data)
            modules_written += 1
            for i, act_data in enumerate(mod_data["activities"]):
                await _upsert_activity(db, module.id, i, act_data)
                activities_written += 1
        await db.commit()

    print(f"wrote {modules_written} modules, {activities_written} activities "
          f"(all is_published=False — media URLs still need filling in)")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
