"""Fix the two failure modes surfaced by audit_lesson_exercises.py, for
every lesson, not just the matching-exercise rollout's own recent work:

  1. ORPHANED: an Exercise row exists for a lesson but has no stub in the
     LIVE sections_json exercise section — invisible to every student
     regardless of language. Predates this session (rows dated 2026-07-13
     and 2026-08-20 were found orphaned) — an earlier content-addition
     never appended its stub, the same class of bug
     attach_matching_to_sections.py's docstring describes, just from a
     different, earlier piece of work.
  2. RU-STALE: an exercise IS referenced in the live sections_json but
     missing from the cached RU translation of it (translation_cache
     entity_type='lesson', field_name='sections_json') — invisible to
     Russian-language students only. Same bug class as
     fix_ru_sections_cache_bulk.py, generalized to every lesson instead of
     just the matching-exercise lessons that script covered.

Purely additive both ways: only ever APPENDS a missing {"id": N} stub,
never removes or reorders an existing entry. Safe to re-run — recomputes
what's missing from the current DB/cache state each time, so a partial
prior run just means less work the second time.
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
        lessons = (await db.execute(select(Lesson))).scalars().all()
        lessons_by_id = {l.id: l for l in lessons}

        all_exercises = (await db.execute(select(Exercise.id, Exercise.lesson_id))).all()
        exercises_by_lesson: dict[int, set[int]] = {}
        for ex_id, lesson_id in all_exercises:
            exercises_by_lesson.setdefault(lesson_id, set()).add(ex_id)

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

        fixed_live = 0
        fixed_ru = 0
        skipped_no_section = []

        for lesson_id, db_ex_ids in exercises_by_lesson.items():
            lesson = lessons_by_id.get(lesson_id)
            if lesson is None or not lesson.sections_json:
                continue
            try:
                sections = json.loads(lesson.sections_json)
            except Exception:
                continue
            ex_sections = [s for s in sections if s.get("type") == "exercise"]
            if len(ex_sections) != 1:
                # 0 sections: covered by the live-fetch fallback (lesson 604
                # precedent) — nothing to append to. >1: didn't occur in the
                # audit: skip either way rather than guess which section.
                if len(ex_sections) == 0 and db_ex_ids:
                    skipped_no_section.append(lesson_id)
                continue
            sec = ex_sections[0]
            live_ids = {e.get("id") for e in sec.get("exercises", [])}

            missing_live = sorted(db_ex_ids - live_ids)
            if missing_live:
                sec.setdefault("exercises", []).extend({"id": i} for i in missing_live)
                lesson.sections_json = json.dumps(sections, ensure_ascii=False)
                fixed_live += 1
                # Re-read for the RU step below so it mirrors the corrected live state.
                live_ids = live_ids | set(missing_live)

            ru_row = ru_cache_by_lesson.get(lesson_id)
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
            ru_ids = {e.get("id") for e in ru_sec.get("exercises", [])}
            missing_ru = sorted(live_ids - ru_ids)
            if missing_ru:
                ru_sec.setdefault("exercises", []).extend({"id": i} for i in missing_ru)
                ru_row.translated_text = json.dumps(ru_sections, ensure_ascii=False)
                ru_row.source_text_hash = _hash_source(lesson.sections_json)
                fixed_ru += 1

        await db.commit()
        print(f"DONE. live sections_json fixed: {fixed_live} lessons; "
              f"RU cache fixed: {fixed_ru} lessons; "
              f"skipped (no exercise section, relies on live-fetch fallback): {skipped_no_section}")


if __name__ == "__main__":
    asyncio.run(main())
