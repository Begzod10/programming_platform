"""Deactivate exercise rows that no lesson's sections_json references.

Re-running the content-enrichment scripts creates a fresh batch of exercise
rows for a lesson without deactivating the previous batch, so old rows pile
up in the `exercises` table. Students never see them (the frontend only
renders whatever `sections_json` declares), but they inflate the table and
show up in admin exports/grading tools. This script finds those orphans and
soft-deletes them (is_active = False) rather than hard-deleting, so the data
is recoverable if a lesson turns out to reference them after all.

Usage:
    python -m scripts.cleanup_orphaned_exercises            # dry-run (default)
    python -m scripts.cleanup_orphaned_exercises --apply    # commit changes
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401 — ensure all mappers registered
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402


def _declared_exercise_ids(sections_json: str | None) -> set[int]:
    if not sections_json:
        return set()
    try:
        sections = json.loads(sections_json)
    except json.JSONDecodeError:
        return set()
    if not isinstance(sections, list):
        return set()

    ids: set[int] = set()
    for section in sections:
        if not isinstance(section, dict) or section.get("type") != "exercise":
            continue
        for entry in section.get("exercises", []):
            if isinstance(entry, dict) and isinstance(entry.get("id"), int):
                ids.add(entry["id"])
    return ids


async def cleanup(apply: bool) -> None:
    label = "APPLY" if apply else "DRY-RUN"
    print(f"=== Cleanup orphaned exercises ({label}) ===\n")

    async with AsyncSessionLocal() as db:
        lessons = (await db.execute(select(Lesson.id, Lesson.title, Lesson.sections_json))).all()
        declared_by_lesson = {
            lesson_id: _declared_exercise_ids(sections_json)
            for lesson_id, _title, sections_json in lessons
        }
        lesson_titles = {lesson_id: title for lesson_id, title, _sections_json in lessons}

        exercises = (
            await db.execute(select(Exercise).where(Exercise.is_active.is_(True)))
        ).scalars().all()

        orphans = [
            ex for ex in exercises
            if ex.id not in declared_by_lesson.get(ex.lesson_id, set())
        ]

        if not orphans:
            print("No orphaned exercises found.")
            return

        by_lesson: dict[int, list[Exercise]] = {}
        for ex in orphans:
            by_lesson.setdefault(ex.lesson_id, []).append(ex)

        for lesson_id, rows in sorted(by_lesson.items()):
            title = lesson_titles.get(lesson_id, "?")
            ids = ", ".join(str(r.id) for r in sorted(rows, key=lambda r: r.id))
            print(f"  lesson_id={lesson_id:>4} ({title}): {len(rows)} orphaned — ids [{ids}]")
            if apply:
                for row in rows:
                    row.is_active = False

        if apply:
            await db.commit()

        print(f"\n--- Summary ---")
        print(f"  lessons_affected: {len(by_lesson)}")
        print(f"  orphaned_exercises: {len(orphans)}")
        if not apply:
            print("\n(dry-run — no changes written. Re-run with --apply to commit.)")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--apply", action="store_true",
                   help="Actually write to the DB. Default is dry-run.")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(cleanup(apply=args.apply))
