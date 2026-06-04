"""Refresh the existing 'Javascript' course (id ~22) to match seed_javascript_course.py.

Unlike refresh_flask_text.py, this script also INSERTS new exercises that exist
in the seed but not in the DB — required because the seed adds 5 new exercises
to L4 (for/while) and a project task to L0.

What this script touches:
  - Lesson: title (fixes L14's broken title), text_content, code_content,
    video_url, sections_json, task_* fields
  - Exercise: text fields on existing rows (matched by `order`)
  - Exercise: INSERTS new rows for orders that exist in seed but not in DB

What this script NEVER touches:
  - Student submissions, completions, video_watches, rankings
  - Lesson order, points_reward, is_active, is_published
  - Exercise correctness fields (correct_answers, correct_order, etc.) on
    EXISTING rows — only text fields are updated. New rows get full data.

Matching keys:
  - Lesson by `order` (stable even when title changes — L14 needs this)
  - Exercise by TITLE within a lesson. The Javascript course has every
    exercise stored with order=0, so matching by `order` would collapse
    them all to one row. Title is unique within a lesson and stable across
    refresh runs. Each matched exercise also gets its `order` reassigned
    to its sequential position in the seed, so the frontend displays them
    in a deterministic order.

Idempotent: a second run is a no-op.

Usage:
    cd backend
    python scripts/refresh_javascript_text.py            # dry-run (default)
    python scripts/refresh_javascript_text.py --apply    # actually write
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402

from scripts.seed_javascript_course import (  # noqa: E402
    COURSE, LESSONS, LESSON_TASKS, build_sections_json, _jdump,
)


# Field name → callable that derives target value from the seed exercise dict.
# Lessons where DB exercises that are NOT in the seed get deleted. Only set
# this for lessons whose existing exercises are known-broken placeholders.
# L4 (for/while) had a single garbage exercise titled "1-savol:".
ORPHAN_DELETE_LESSONS = {4}


EXERCISE_TEXT_FIELDS = {
    "title": lambda ex: ex["title"],
    "description": lambda ex: ex.get("description", ex["title"]),
    "options": lambda ex: _jdump(ex.get("options")),
    "hint": lambda ex: ex.get("hint", ""),
    "explanation": lambda ex: ex.get("explanation", ""),
    "expected_answer": lambda ex: ex.get("expected_answer", ""),
}


def _norm(v) -> str:
    return "" if v is None else str(v)


async def refresh(apply: bool) -> None:
    label = "APPLY" if apply else "DRY-RUN"
    print(f"=== Javascript Refresh ({label}) ===\n")

    async with AsyncSessionLocal() as db:
        course = (
            await db.execute(select(Course).where(Course.title == COURSE["title"]))
        ).scalar_one_or_none()
        if not course:
            raise SystemExit(
                f"Course {COURSE['title']!r} not found. Run seed_javascript_course.py first."
            )
        print(f"Course id={course.id}  title={course.title!r}\n")

        lessons_by_order = {
            l.order: l for l in (
                await db.execute(select(Lesson).where(Lesson.course_id == course.id))
            ).scalars().all()
        }
        print(f"DB has {len(lessons_by_order)} lessons.\n")

        total_lesson_fields = 0
        total_ex_field_updates = 0
        total_ex_inserts = 0

        for ldata in LESSONS:
            order = ldata["order"]
            lesson = lessons_by_order.get(order)
            if not lesson:
                print(f"  ⚠️  order={order} {ldata['title'][:40]!r} — missing in DB, skipped")
                continue

            lesson_changes: list[tuple[str, str, str]] = []
            task = LESSON_TASKS.get(order, {})

            target_fields = [
                ("title", ldata["title"]),
                ("text_content", ldata["text"]),
                ("code_content", ldata["code"]),
                ("video_url", ldata.get("video") or None),
                ("task_title", task.get("title")),
                ("task_description", task.get("description")),
                ("task_requirements", task.get("requirements")),
                ("task_technologies", task.get("technologies")),
                ("task_deadline_days", task.get("deadline_days")),
            ]
            for field, new_value in target_fields:
                cur = getattr(lesson, field)
                if _norm(cur) != _norm(new_value):
                    lesson_changes.append((field, _norm(cur)[:60], _norm(new_value)[:60]))
                    if apply:
                        setattr(lesson, field, new_value)

            # Match by title — every exercise has order=0 in the DB so position
            # is unreliable. Title is unique within a lesson.
            existing_ex_list = (
                await db.execute(
                    select(Exercise)
                    .where(Exercise.lesson_id == lesson.id)
                    .order_by(Exercise.id)
                )
            ).scalars().all()
            existing_by_title = {e.title: e for e in existing_ex_list}

            ex_changes_count = 0
            ex_inserts_count = 0
            order_reassigns = 0
            ex_deletes_count = 0
            seed_titles = {ex["title"] for ex in ldata["exercises"]}
            if order in ORPHAN_DELETE_LESSONS:
                for row in existing_ex_list:
                    if row.title not in seed_titles:
                        ex_deletes_count += 1
                        if apply:
                            await db.delete(row)

            for seed_order, ex_data in enumerate(ldata["exercises"]):
                row = existing_by_title.get(ex_data["title"])
                if row is None:
                    # NEW exercise — insert
                    ex_inserts_count += 1
                    if apply:
                        new_row = Exercise(
                            lesson_id=lesson.id,
                            title=ex_data["title"],
                            description=ex_data.get("description", ex_data["title"]),
                            exercise_type=ex_data["exercise_type"],
                            options=_jdump(ex_data.get("options")),
                            correct_answers=_jdump(ex_data.get("correct_answers")),
                            drag_items=_jdump(ex_data.get("drag_items")),
                            correct_order=_jdump(ex_data.get("correct_order")),
                            is_multiple_select=bool(ex_data.get("is_multiple_select", False)),
                            expected_answer=ex_data.get("expected_answer", ""),
                            hint=ex_data.get("hint", ""),
                            explanation=ex_data.get("explanation", ""),
                            difficulty_level=ex_data["difficulty_level"],
                            points=ex_data["points"],
                            order=seed_order,
                            is_active=True,
                        )
                        db.add(new_row)
                    continue

                # EXISTING — update text-only fields
                for field, derive in EXERCISE_TEXT_FIELDS.items():
                    new_value = derive(ex_data)
                    cur = getattr(row, field)
                    if _norm(cur) != _norm(new_value):
                        ex_changes_count += 1
                        if apply:
                            setattr(row, field, new_value)
                # Reassign sequential order so the frontend reads them in a
                # stable order. (Existing DB has all rows at order=0.)
                if row.order != seed_order:
                    order_reassigns += 1
                    if apply:
                        row.order = seed_order

            if lesson_changes or ex_changes_count or ex_inserts_count or order_reassigns or ex_deletes_count:
                print(f"  📝 order={order:>2} {lesson.title[:50]}")
                for field, old, new in lesson_changes:
                    if field in ("text_content", "code_content", "task_requirements"):
                        print(f"     • {field}: len {len(_norm(getattr(lesson, field)))} → updated")
                    else:
                        print(f"     • {field}: {old!r} → {new!r}")
                if ex_changes_count:
                    print(f"     • {ex_changes_count} exercise text fields updated")
                if order_reassigns:
                    print(f"     • {order_reassigns} exercise order values reassigned")
                if ex_inserts_count:
                    print(f"     • {ex_inserts_count} NEW exercises inserted")
                if ex_deletes_count:
                    print(f"     • {ex_deletes_count} ORPHAN exercises deleted")
                total_lesson_fields += len(lesson_changes)
                total_ex_field_updates += ex_changes_count
                total_ex_inserts += ex_inserts_count

            if apply and (lesson_changes or ex_changes_count or ex_inserts_count or order_reassigns or ex_deletes_count):
                await db.flush()
                fresh = {
                    e.order: e for e in (
                        await db.execute(
                            select(Exercise).where(Exercise.lesson_id == lesson.id).order_by(Exercise.order)
                        )
                    ).scalars().all()
                }
                ordered = [fresh[i] for i in sorted(fresh)]
                lesson.sections_json = build_sections_json(ldata, ordered)

        print(f"\n--- Summary ---")
        print(f"  Lesson field updates:    {total_lesson_fields}")
        print(f"  Exercise text updates:   {total_ex_field_updates}")
        print(f"  Exercise inserts (NEW):  {total_ex_inserts}")

        if not (total_lesson_fields or total_ex_field_updates or total_ex_inserts) and total_ex_inserts == 0:
            print("\n✓ Nothing to refresh — DB matches seed.")
            await db.rollback()
            return

        if apply:
            await db.commit()
            print("\n✓ APPLIED.")
        else:
            await db.rollback()
            print("\nDRY-RUN: nothing written. Re-run with --apply to commit.")

    await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="Actually write changes (default is dry-run).")
    args = parser.parse_args()
    asyncio.run(refresh(apply=args.apply))


if __name__ == "__main__":
    main()
