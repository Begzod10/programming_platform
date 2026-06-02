"""Refresh lesson and exercise TEXT content to match the local seed file.

Use case: you edit `seed_flask_course.py` (typo fix, wording change, hint
clarification) and want to push those edits to the live course WITHOUT
re-inserting lessons or touching student progress.

What this script touches:
  - Lesson: text_content, code_content, video_url
  - Exercise: title, description, options, hint, explanation, expected_answer
  - Lesson: sections_json (rebuilt for any lesson whose text changed)

What this script NEVER touches:
  - Lesson: order, points_reward, task_* fields, is_active, is_published
  - Exercise: exercise_type, correct_answers, drag_items, correct_order,
    is_multiple_select, difficulty_level, points, order, is_active
  - Submissions, completions, video_watches, student rankings

Matching keys (must stay stable across edits):
  - Lesson by title       (unique within a course)
  - Exercise by `order`   (unique within a lesson)

Idempotent: a second run is a no-op.

Usage:
    cd backend
    python scripts/refresh_flask_text.py            # dry-run (default)
    python scripts/refresh_flask_text.py --apply    # actually write
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401 ensure all models registered
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402

from scripts.seed_flask_course import (  # noqa: E402
    COURSE,
    LESSONS,
    build_sections_json,
    _jdump,
)


# (field name → callable that derives the target value from the ex dict)
EXERCISE_TEXT_FIELDS = {
    "title": lambda ex: ex["title"],
    "description": lambda ex: ex.get("description", ex["title"]),
    "options": lambda ex: _jdump(ex.get("options")),
    "hint": lambda ex: ex.get("hint", ""),
    "explanation": lambda ex: ex.get("explanation", ""),
    "expected_answer": lambda ex: ex.get("expected_answer", ""),
}


async def _load_course(db: AsyncSession) -> Course:
    res = await db.execute(select(Course).where(Course.title == COURSE["title"]))
    course = res.scalar_one_or_none()
    if not course:
        raise SystemExit(
            f"Course '{COURSE['title']}' not found. Run seed_flask_course.py first."
        )
    return course


async def _load_lessons_by_title(db: AsyncSession, course_id: int) -> dict[str, Lesson]:
    res = await db.execute(select(Lesson).where(Lesson.course_id == course_id))
    return {l.title: l for l in res.scalars().all()}


async def _load_exercises_by_order(db: AsyncSession, lesson_id: int) -> dict[int, Exercise]:
    res = await db.execute(
        select(Exercise).where(Exercise.lesson_id == lesson_id).order_by(Exercise.order)
    )
    return {e.order: e for e in res.scalars().all()}


def _normalize(value) -> str:
    """Coerce DB and seed values to comparable strings (both can be None/empty)."""
    return "" if value is None else str(value)


async def refresh(apply: bool) -> None:
    label = "APPLY" if apply else "DRY-RUN"
    print(f"=== Flask Text Refresh ({label}) ===\n")

    async with AsyncSessionLocal() as db:
        course = await _load_course(db)
        existing = await _load_lessons_by_title(db, course.id)
        print(f"Course id={course.id}  lessons in DB: {len(existing)}\n")

        # Lessons that exist in the seed but not yet in the DB are reported
        # but not inserted — that's what upgrade_flask_revisions.py is for.
        missing_in_db = [l["title"] for l in LESSONS if l["title"] not in existing]
        if missing_in_db:
            print("⚠️  Lessons in seed but NOT in DB (run upgrade script first):")
            for t in missing_in_db:
                print(f"   • {t}")
            print()

        total_lesson_changes = 0
        total_exercise_changes = 0
        lessons_needing_sections_rebuild: set[int] = set()

        for ldata in LESSONS:
            lesson = existing.get(ldata["title"])
            if not lesson:
                continue

            lesson_changes: list[tuple[str, str, str]] = []

            # Lesson text/code/video
            for field, new_value in [
                ("text_content", ldata["text"]),
                ("code_content", ldata["code"]),
                ("video_url", ldata.get("video") or None),
            ]:
                current = getattr(lesson, field)
                # Normalize None vs "" so we don't churn on equivalent emptiness.
                if _normalize(current) != _normalize(new_value):
                    lesson_changes.append((field, _normalize(current), _normalize(new_value)))
                    if apply:
                        setattr(lesson, field, new_value)

            # Exercises (match by order within this lesson)
            ex_existing = await _load_exercises_by_order(db, lesson.id)
            ex_change_count = 0
            for ex_order, ex_data in enumerate(ldata["exercises"]):
                ex = ex_existing.get(ex_order)
                if ex is None:
                    print(f"   ⚠️  '{ldata['title']}'  exercise order={ex_order} missing in DB — skipped")
                    continue
                for field, derive in EXERCISE_TEXT_FIELDS.items():
                    new_value = derive(ex_data)
                    current = getattr(ex, field)
                    if _normalize(current) != _normalize(new_value):
                        ex_change_count += 1
                        if apply:
                            setattr(ex, field, new_value)

            # Report
            if lesson_changes or ex_change_count > 0:
                print(f"  📝 '{ldata['title']}'  ({len(lesson_changes)} lesson fields, {ex_change_count} exercise fields)")
                for field, old, new in lesson_changes:
                    # Short preview only — these strings are HUGE for text_content.
                    snippet = _diff_snippet(old, new)
                    print(f"     • {field}: {snippet}")
                lessons_needing_sections_rebuild.add(lesson.id)
                total_lesson_changes += len(lesson_changes)
                total_exercise_changes += ex_change_count

            # Always rebuild sections_json when ANY exercise text changed in this
            # lesson, since sections_json embeds exercise titles/options/hints.
            if (lesson_changes or ex_change_count > 0) and apply:
                fresh_ex = await _load_exercises_by_order(db, lesson.id)
                ordered_ex = [fresh_ex[i] for i in sorted(fresh_ex)]
                lesson.sections_json = build_sections_json(ldata, ordered_ex)

        if total_lesson_changes == 0 and total_exercise_changes == 0:
            print("✓ Nothing to refresh — DB text matches the seed file exactly.")
            return

        print(f"\n--- Summary ---")
        print(f"  Lesson fields to update:   {total_lesson_changes}")
        print(f"  Exercise fields to update: {total_exercise_changes}")
        print(f"  sections_json rebuilds:    {len(lessons_needing_sections_rebuild)}")

        if apply:
            await db.commit()
            print(f"\n✓ APPLIED.")
        else:
            await db.rollback()
            print(f"\nDRY-RUN: nothing written. Re-run with --apply to commit.")


def _diff_snippet(old: str, new: str, width: int = 80) -> str:
    """One-line summary showing where strings diverge."""
    if len(old) <= width and len(new) <= width:
        return f"'{old}' → '{new}'"
    # Find first differing character to anchor the snippet.
    i = 0
    while i < min(len(old), len(new)) and old[i] == new[i]:
        i += 1
    start = max(0, i - 20)
    return (f"len {len(old)}→{len(new)}, differs at char {i}: "
            f"'...{old[start:start+40]}' → '...{new[start:start+40]}'")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="Actually write changes (default is dry-run).")
    args = parser.parse_args()
    asyncio.run(refresh(apply=args.apply))


if __name__ == "__main__":
    main()
