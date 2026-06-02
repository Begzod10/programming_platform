"""Add R1/R2/R3 revision lessons to an EXISTING "Python Flask" course.

Non-destructive: never edits existing lesson content/exercises/student data.
Only writes:
  1. UPDATE lessons SET "order" = ... WHERE id IN (...)
     — shifts existing lesson orders to make room for revisions.
  2. INSERT INTO lessons + exercises for R1, R2, R3 if missing.

Idempotent: safe to re-run. Detects existing R1/R2/R3 by title prefix and
skips re-inserting them.

Usage:
    cd backend
    python scripts/upgrade_flask_revisions.py            # dry-run (default)
    python scripts/upgrade_flask_revisions.py --apply    # actually write

The script reads R1_TEXT/R2_TEXT/etc. and the 3 new lesson dicts directly
from seed_flask_course.LESSONS, so the two files stay in sync.
"""
from __future__ import annotations

import argparse
import asyncio
import json
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

# Re-use the authoritative content from the seed script so we never drift.
from scripts.seed_flask_course import (  # noqa: E402
    COURSE,
    LESSONS,
    LESSON_TASKS,
    build_sections_json,
    _jdump,
)


REVISION_TITLE_PREFIX = "R"  # R1-..., R2-..., R3-...


def _is_revision(title: str) -> bool:
    """Match the R1/R2/R3 titles we plan to insert."""
    if not title or len(title) < 3:
        return False
    return title[0] == "R" and title[1].isdigit() and title[2] == "-"


async def _load_course(db: AsyncSession) -> Course:
    res = await db.execute(select(Course).where(Course.title == COURSE["title"]))
    course = res.scalar_one_or_none()
    if not course:
        raise SystemExit(
            f"Course '{COURSE['title']}' not found. Run seed_flask_course.py first."
        )
    return course


async def _load_existing_lessons(db: AsyncSession, course_id: int) -> list[Lesson]:
    res = await db.execute(
        select(Lesson).where(Lesson.course_id == course_id).order_by(Lesson.order)
    )
    return list(res.scalars().all())


async def _shift_orders(
    db: AsyncSession,
    existing: list[Lesson],
    target_by_title: dict[str, int],
    *,
    apply: bool,
) -> int:
    """Update existing lessons to their target orders.

    Two-phase update to avoid unique-constraint collisions on (course_id, order):
    bump every shifted lesson into a temporary high range first, then drop
    them into their final positions. The actual DB column has no such
    constraint right now, but the two-phase approach is safe even if one is
    added later, and keeps prod sane during the transaction.
    """
    if not apply:
        # In dry-run, just report what would change.
        changes = 0
        for lesson in existing:
            target = target_by_title.get(lesson.title)
            if target is None:
                continue
            if lesson.order != target:
                print(f"  WOULD SHIFT: '{lesson.title}'  order {lesson.order} → {target}")
                changes += 1
        return changes

    # Phase 1: park anything that needs to move into a high temporary slot.
    TEMP_OFFSET = 1000
    phase1 = 0
    for lesson in existing:
        target = target_by_title.get(lesson.title)
        if target is not None and lesson.order != target:
            lesson.order = lesson.order + TEMP_OFFSET
            phase1 += 1
    await db.flush()

    # Phase 2: drop them into their final positions.
    for lesson in existing:
        target = target_by_title.get(lesson.title)
        if target is not None and lesson.order != target:
            lesson.order = target
    await db.flush()
    return phase1


async def _insert_revision_lesson(
    db: AsyncSession,
    course_id: int,
    ldata: dict,
    *,
    apply: bool,
) -> int:
    task = LESSON_TASKS.get(ldata["order"], {})
    if not apply:
        print(
            f"  WOULD INSERT: order={ldata['order']:>2}  "
            f"{ldata['title']}  ({len(ldata['exercises'])} exercises)"
        )
        if task.get("title"):
            print(f"               mini-project: {task['title']}")
        return 0

    lesson = Lesson(
        course_id=course_id,
        title=ldata["title"],
        order=ldata["order"],
        points_reward=10,
        text_content=ldata["text"],
        code_content=ldata["code"],
        code_language=ldata["lang"],
        video_url=ldata["video"] or None,
        sections_json=None,
        task_title=task.get("title"),
        task_description=task.get("description"),
        task_requirements=task.get("requirements"),
        task_technologies=task.get("technologies"),
        task_deadline_days=task.get("deadline_days"),
        is_active=True,
        is_published=True,
    )
    db.add(lesson)
    await db.flush()

    ex_rows: list[Exercise] = []
    for ex_order, ex in enumerate(ldata["exercises"]):
        row = Exercise(
            lesson_id=lesson.id,
            title=ex["title"],
            description=ex.get("description", ex["title"]),
            exercise_type=ex["exercise_type"],
            options=_jdump(ex.get("options")),
            correct_answers=_jdump(ex.get("correct_answers")),
            drag_items=_jdump(ex.get("drag_items")),
            correct_order=_jdump(ex.get("correct_order")),
            is_multiple_select=bool(ex.get("is_multiple_select", False)),
            expected_answer=ex.get("expected_answer", ""),
            hint=ex.get("hint", ""),
            explanation=ex.get("explanation", ""),
            difficulty_level=ex["difficulty_level"],
            points=ex["points"],
            order=ex_order,
            is_active=True,
        )
        db.add(row)
        ex_rows.append(row)
    await db.flush()

    lesson.sections_json = build_sections_json(ldata, ex_rows)
    print(
        f"  INSERTED: order={lesson.order:>2}  id={lesson.id:>3}  "
        f"{lesson.title}  ({len(ex_rows)} exercises)"
    )
    return 1


async def upgrade(apply: bool) -> None:
    label = "APPLY" if apply else "DRY-RUN"
    print(f"=== Flask Revisions Upgrade ({label}) ===\n")

    async with AsyncSessionLocal() as db:
        course = await _load_course(db)
        print(f"Course id={course.id}  title='{course.title}'")

        existing = await _load_existing_lessons(db, course.id)
        existing_titles = {l.title for l in existing}
        print(f"Existing lessons: {len(existing)}")

        # Build target order map from the new LESSONS list (titles → target order).
        target_by_title = {l["title"]: l["order"] for l in LESSONS}

        # ─── Step 1: detect missing revisions ─────────────────────────
        revisions_to_insert = [
            l for l in LESSONS
            if _is_revision(l["title"]) and l["title"] not in existing_titles
        ]
        print(f"\nRevisions to insert: {len(revisions_to_insert)}")
        for r in revisions_to_insert:
            print(f"  • {r['title']}  → target order={r['order']}")

        already_present = [
            l["title"] for l in LESSONS
            if _is_revision(l["title"]) and l["title"] in existing_titles
        ]
        if already_present:
            print(f"\nRevisions already present (will skip insert): {already_present}")

        # ─── Step 2: detect order shifts needed for existing lessons ─
        print("\nOrder shifts needed:")
        shifts_needed = 0
        for lesson in existing:
            target = target_by_title.get(lesson.title)
            if target is None:
                # An existing lesson that we don't recognize — leave it alone.
                print(f"  UNKNOWN existing lesson (left alone): '{lesson.title}'  order={lesson.order}")
                continue
            if lesson.order != target:
                shifts_needed += 1

        if shifts_needed == 0 and not revisions_to_insert:
            print("\n✓ Nothing to do — course is already at the target structure.")
            return

        # ─── Step 3: execute the shifts ───────────────────────────────
        print(f"\n--- Shifting orders ({shifts_needed} lessons) ---")
        await _shift_orders(db, existing, target_by_title, apply=apply)

        # ─── Step 4: insert missing revisions ─────────────────────────
        print(f"\n--- Inserting revisions ({len(revisions_to_insert)} lessons) ---")
        inserted = 0
        for r in revisions_to_insert:
            inserted += await _insert_revision_lesson(db, course.id, r, apply=apply)

        # ─── Step 5: commit or rollback ───────────────────────────────
        if apply:
            await db.commit()
            print(
                f"\n✓ APPLIED: shifted {shifts_needed} orders, inserted {inserted} revisions. "
                f"Course now has {len(existing) + inserted} lessons."
            )
        else:
            await db.rollback()
            print(
                f"\nDRY-RUN: would shift {shifts_needed} orders, insert "
                f"{len(revisions_to_insert)} revisions. "
                f"Run with --apply to commit."
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write changes (default is dry-run).",
    )
    args = parser.parse_args()
    asyncio.run(upgrade(apply=args.apply))


if __name__ == "__main__":
    main()
