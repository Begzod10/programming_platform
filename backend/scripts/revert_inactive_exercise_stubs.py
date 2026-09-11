"""Revert a mistake made by fix_orphaned_exercises.py: it treated any
Exercise row missing from a lesson's sections_json exercise section as a
bug and appended a stub for it — but every single one of those "orphaned"
exercises turned out to be `is_active = False`: an old draft/superseded
exercise that was DELIBERATELY deactivated and correctly left out of
sections_json, not an accidentally-orphaned one. audit_lesson_exercises.py
never checked is_active, so it flagged 51 lessons' worth of intentional
exclusions as bugs, and the fix script resurrected them into every
affected lesson's live AND cached-RU exercise list.

This removes exactly those stub entries — matched by id against
Exercise.is_active == False, computed fresh from the DB, never a
hand-typed id list — from both places, leaving everything else the
fix script legitimately added (the RU-cache sync for exercises that
genuinely ARE active and were only missing from the translation) intact.
"""
from __future__ import annotations

import asyncio
import json
import sys

sys.path.insert(0, "/home/student_platform/backend")

from sqlalchemy import select  # noqa: E402

from app.db import base as _all_models  # noqa: E402,F401
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.translation_cache import TranslationCache  # noqa: E402
from app.services.translation_service import _hash_source  # noqa: E402


async def main():
    async with AsyncSessionLocal() as db:
        inactive_ids = set(
            (await db.execute(select(Exercise.id).where(Exercise.is_active.is_(False)))).scalars().all()
        )
        print(f"{len(inactive_ids)} inactive exercises in the DB total")

        lessons = (await db.execute(select(Lesson))).scalars().all()

        ru_cache_rows = (
            await db.execute(
                select(TranslationCache).where(
                    TranslationCache.entity_type == "lesson",
                    TranslationCache.lang == "ru",
                    TranslationCache.field_name == "sections_json",
                )
            )
        ).scalars().all()
        ru_cache_by_lesson = {row.entity_id: row for row in ru_cache_rows}

        reverted_live = 0
        reverted_ru = 0

        for lesson in lessons:
            if not lesson.sections_json:
                continue
            try:
                sections = json.loads(lesson.sections_json)
            except Exception:
                continue
            ex_sections = [s for s in sections if s.get("type") == "exercise"]
            if len(ex_sections) != 1:
                continue
            sec = ex_sections[0]
            entries = sec.get("exercises", [])
            kept = [e for e in entries if e.get("id") not in inactive_ids]
            if len(kept) != len(entries):
                removed = [e.get("id") for e in entries if e.get("id") in inactive_ids]
                sec["exercises"] = kept
                lesson.sections_json = json.dumps(sections, ensure_ascii=False)
                reverted_live += 1
                print(f"lesson {lesson.id}: removed inactive stub(s) {removed} from live sections_json")

            ru_row = ru_cache_by_lesson.get(lesson.id)
            if ru_row is None:
                continue
            try:
                ru_sections = json.loads(ru_row.translated_text)
            except Exception:
                continue
            ru_ex_sections = [s for s in ru_sections if s.get("type") == "exercise"]
            if len(ru_ex_sections) != 1:
                continue
            ru_sec = ru_ex_sections[0]
            ru_entries = ru_sec.get("exercises", [])
            ru_kept = [e for e in ru_entries if e.get("id") not in inactive_ids]
            if len(ru_kept) != len(ru_entries):
                ru_sec["exercises"] = ru_kept
                ru_row.translated_text = json.dumps(ru_sections, ensure_ascii=False)
                ru_row.source_text_hash = _hash_source(lesson.sections_json)
                reverted_ru += 1

        await db.commit()
        print(f"\nDONE. reverted live: {reverted_live} lessons; reverted RU cache: {reverted_ru} lessons")


if __name__ == "__main__":
    asyncio.run(main())
