"""Platform-wide audit: for every lesson, compare (a) which Exercise rows
actually exist for it in the DB against (b) which exercise ids its
sections_json exercise section references, on BOTH the live column and (for
lang=ru) the cached translation_cache blob — the same three failure modes
this session already found and fixed once for the matching-exercise
rollout, checked here across every exercise of every type, not just
matching:

  1. ORPHANED: an Exercise row exists for this lesson but no stub for it
     appears in the LIVE sections_json exercise section at all — invisible
     to every student regardless of language.
  2. RU-STALE: it IS in the live column but missing from the cached RU
     sections_json translation — invisible to Russian-language students
     only (the translation_store bug class).
  3. DANGLING: sections_json references an exercise id that doesn't exist
     in the exercises table at all (would 404/error at hydration time).
  4. ZERO_EXERCISES: the lesson has no exercise-type section, and no
     Exercise rows either — nothing to show (may be legitimate for a pure
     project/capstone lesson; flagged for manual judgment, not assumed bad).
  5. NO_EXERCISE_SECTION_BUT_HAS_EXERCISES: no exercise-type section in
     sections_json at all, but Exercise rows exist — relies entirely on
     StudentCourses.js's live-fetch fallback (confirmed correct for lesson
     604, but worth surfacing every instance so it's a known list, not a
     surprise).
  6. REFERENCED_BUT_INACTIVE: sections_json references an exercise whose
     `is_active` is False — the opposite mistake from ORPHANED, and the one
     this script's first version made by omission: `is_active = False`
     Exercise rows (old drafts deliberately superseded/deactivated — 112 of
     them exist platform-wide) are CORRECTLY excluded from sections_json,
     not a bug. Only a row referenced here despite being inactive is worth
     flagging.

Only ACTIVE exercises (is_active is not False) count toward what "should"
be referenced for ORPHANED/RU-STALE — never flag an intentionally
deactivated exercise as missing.
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


async def main():
    async with AsyncSessionLocal() as db:
        lessons = (await db.execute(select(Lesson))).scalars().all()
        print(f"auditing {len(lessons)} lessons...")

        all_exercises = (await db.execute(select(Exercise.id, Exercise.lesson_id, Exercise.is_active))).all()
        exercises_by_lesson: dict[int, set[int]] = {}       # ACTIVE only — what should be referenced
        all_exercise_ids_by_lesson: dict[int, set[int]] = {}  # active + inactive — for dangling-ref checks
        all_exercise_ids: set[int] = set()
        inactive_ids: set[int] = set()
        for ex_id, lesson_id, is_active in all_exercises:
            all_exercise_ids_by_lesson.setdefault(lesson_id, set()).add(ex_id)
            all_exercise_ids.add(ex_id)
            if is_active:
                exercises_by_lesson.setdefault(lesson_id, set()).add(ex_id)
            else:
                inactive_ids.add(ex_id)
        print(f"({len(inactive_ids)} inactive exercises excluded from the 'should be referenced' set)")

        ru_cache_rows = (
            await db.execute(
                select(TranslationCache.entity_id, TranslationCache.translated_text).where(
                    TranslationCache.entity_type == "lesson",
                    TranslationCache.lang == "ru",
                    TranslationCache.field_name == "sections_json",
                )
            )
        ).all()
        ru_cache_by_lesson = {entity_id: text for entity_id, text in ru_cache_rows}

        orphaned = []          # (lesson_id, missing_ex_ids) — live column
        ru_stale = []          # (lesson_id, missing_ex_ids) — RU cache only
        dangling = []          # (lesson_id, dangling_ids)
        zero_exercises = []    # lesson_id
        no_section_but_has_ex = []  # (lesson_id, ex_ids)
        multi_exercise_section = []  # lesson_id, count — structural oddity worth flagging
        referenced_but_inactive = []  # (lesson_id, inactive_ex_ids) — the opposite mistake

        for lesson in lessons:
            db_ex_ids = exercises_by_lesson.get(lesson.id, set())

            if not lesson.sections_json:
                if db_ex_ids:
                    no_section_but_has_ex.append((lesson.id, sorted(db_ex_ids)))
                else:
                    zero_exercises.append(lesson.id)
                continue

            try:
                sections = json.loads(lesson.sections_json)
            except Exception:
                orphaned.append((lesson.id, sorted(db_ex_ids), "INVALID_JSON"))
                continue

            ex_sections = [s for s in sections if s.get("type") == "exercise"]
            if len(ex_sections) == 0:
                if db_ex_ids:
                    no_section_but_has_ex.append((lesson.id, sorted(db_ex_ids)))
                else:
                    zero_exercises.append(lesson.id)
                continue
            if len(ex_sections) > 1:
                multi_exercise_section.append((lesson.id, len(ex_sections)))

            referenced_ids: set[int] = set()
            for sec in ex_sections:
                for e in sec.get("exercises", []):
                    if e.get("id") is not None:
                        referenced_ids.add(e["id"])

            missing_from_section = db_ex_ids - referenced_ids
            if missing_from_section:
                orphaned.append((lesson.id, sorted(missing_from_section)))

            dangling_ids = referenced_ids - all_exercise_ids
            if dangling_ids:
                dangling.append((lesson.id, sorted(dangling_ids)))

            referenced_but_inactive_ids = referenced_ids & inactive_ids
            if referenced_but_inactive_ids:
                referenced_but_inactive.append((lesson.id, sorted(referenced_but_inactive_ids)))

            # RU-cache check, only meaningful when a cache row exists at all
            ru_text = ru_cache_by_lesson.get(lesson.id)
            if ru_text:
                try:
                    ru_sections = json.loads(ru_text)
                except Exception:
                    continue
                ru_ex_sections = [s for s in ru_sections if s.get("type") == "exercise"]
                ru_referenced: set[int] = set()
                for sec in ru_ex_sections:
                    for e in sec.get("exercises", []):
                        if e.get("id") is not None:
                            ru_referenced.add(e["id"])
                ru_missing = db_ex_ids - ru_referenced
                if ru_missing:
                    ru_stale.append((lesson.id, sorted(ru_missing)))

        print(f"\n=== ORPHANED (in DB, missing from LIVE sections_json) — {len(orphaned)} lessons ===")
        for row in orphaned[:50]:
            print(" ", row)
        if len(orphaned) > 50:
            print(f"  ... and {len(orphaned) - 50} more")

        print(f"\n=== RU-STALE (in live column, missing from cached RU translation) — {len(ru_stale)} lessons ===")
        for row in ru_stale[:50]:
            print(" ", row)
        if len(ru_stale) > 50:
            print(f"  ... and {len(ru_stale) - 50} more")

        print(f"\n=== DANGLING (sections_json references a nonexistent exercise id) — {len(dangling)} lessons ===")
        for row in dangling[:50]:
            print(" ", row)

        print(f"\n=== ZERO_EXERCISES (no exercise section, no Exercise rows) — {len(zero_exercises)} lessons ===")
        print(" ", zero_exercises[:80], "..." if len(zero_exercises) > 80 else "")

        print(f"\n=== NO_EXERCISE_SECTION_BUT_HAS_EXERCISES (relies on live-fetch fallback) — {len(no_section_but_has_ex)} lessons ===")
        for row in no_section_but_has_ex[:50]:
            print(" ", row)

        print(f"\n=== MULTIPLE exercise-type sections in one lesson (structural oddity) — {len(multi_exercise_section)} lessons ===")
        for row in multi_exercise_section[:30]:
            print(" ", row)

        print(f"\n=== REFERENCED_BUT_INACTIVE (sections_json points at a deactivated exercise) — {len(referenced_but_inactive)} lessons ===")
        for row in referenced_but_inactive[:50]:
            print(" ", row)

        print("\n=== SUMMARY ===")
        print(f"total lessons: {len(lessons)}")
        print(f"orphaned (live, active only): {len(orphaned)}")
        print(f"ru-stale (active only): {len(ru_stale)}")
        print(f"dangling refs: {len(dangling)}")
        print(f"zero exercises: {len(zero_exercises)}")
        print(f"no-section-but-has-exercises: {len(no_section_but_has_ex)}")
        print(f"multi-exercise-section: {len(multi_exercise_section)}")
        print(f"referenced-but-inactive: {len(referenced_but_inactive)}")


if __name__ == "__main__":
    asyncio.run(main())
