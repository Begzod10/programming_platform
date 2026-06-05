"""Refresh the existing 'Dasturlash dunyosiga kirish' course in-place
to match seed_intro_programming.py.

Same pattern as refresh_javascript_text.py / refresh_html_css_text.py:
  - Matches lessons by `order` (stable across title changes)
  - Matches exercises by TITLE within a lesson (so reordering / order=0
    bug from older courses doesn't scramble matches)
  - Inserts NEW exercises (e.g. when L1 swaps to a different set)
  - Deletes ORPHAN exercises ONLY for lessons listed in
    ORPHAN_DELETE_LESSONS — currently {0} (L1) because the entire
    exercise set was redesigned and the old theory-heavy questions
    have no educational value to preserve
  - Rebuilds sections_json
  - Student submissions / completions / video_watches untouched

Usage:
    cd backend
    python scripts/refresh_intro_programming_text.py            # dry-run
    python scripts/refresh_intro_programming_text.py --apply    # write
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

from scripts.seed_intro_programming import (  # noqa: E402
    COURSE, LESSONS, LESSON_TASKS, build_sections_json, _jdump,
)


# Delete exercises that exist in DB but not in the seed — only for lessons
# whose old exercise set was deliberately replaced.
# L1 (order=0): rewritten from theory to WIN-FIRST DevTools — all 5 swapped.
# L2 (order=1): rewritten with polyglot hands-on hook — all 5 swapped.
# L3 (order=2): rewritten with browser-based machine inspection — 4 swapped,
#               1 kept (absolute vs relative path essay).
# L4 (order=3): rewritten with 3-block JS console hook (sequence/condition/
#               loop on google.com) — 3 swapped, 2 kept by title (the
#               3-blocks mc and the cheksiz-sikl essay).
ORPHAN_DELETE_LESSONS = {0, 1, 2, 3, 4, 5, 6}


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
    print(f"=== Intro Programming Refresh ({label}) ===\n")

    async with AsyncSessionLocal() as db:
        course = (
            await db.execute(select(Course).where(Course.title == COURSE["title"]))
        ).scalar_one_or_none()
        if not course:
            raise SystemExit(
                f"Course {COURSE['title']!r} not found. "
                "Run seed_intro_programming.py first."
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
        total_ex_deletes = 0

        for ldata in LESSONS:
            order = ldata["order"]
            lesson = lessons_by_order.get(order)
            if not lesson:
                print(f"  ⚠️  order={order} missing in DB, skipped")
                continue

            lesson_changes: list[tuple[str, str, str]] = []
            task = LESSON_TASKS.get(order, {})

            target_fields = [
                ("title", ldata["title"]),
                ("text_content", ldata["text"]),
                ("code_content", ldata["code"]),
                ("code_language", ldata["lang"]),
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

                for field, derive in EXERCISE_TEXT_FIELDS.items():
                    new_value = derive(ex_data)
                    cur = getattr(row, field)
                    if _norm(cur) != _norm(new_value):
                        ex_changes_count += 1
                        if apply:
                            setattr(row, field, new_value)
                if row.order != seed_order:
                    order_reassigns += 1
                    if apply:
                        row.order = seed_order

            if lesson_changes or ex_changes_count or ex_inserts_count or order_reassigns or ex_deletes_count:
                print(f"  📝 order={order:>2} {lesson.title[:55]}")
                for field, old, new in lesson_changes:
                    if field in ("text_content", "code_content", "task_requirements", "task_description"):
                        print(f"     • {field}: len {len(_norm(getattr(lesson, field)))} → updated")
                    else:
                        print(f"     • {field}: {old!r} → {new!r}")
                if ex_changes_count:
                    print(f"     • {ex_changes_count} exercise text fields updated")
                if order_reassigns:
                    print(f"     • {order_reassigns} exercise order reassignments")
                if ex_inserts_count:
                    print(f"     • {ex_inserts_count} NEW exercises inserted")
                if ex_deletes_count:
                    print(f"     • {ex_deletes_count} ORPHAN exercises deleted")
                total_lesson_fields += len(lesson_changes)
                total_ex_field_updates += ex_changes_count
                total_ex_inserts += ex_inserts_count
                total_ex_deletes += ex_deletes_count

            if apply and (lesson_changes or ex_changes_count or ex_inserts_count or order_reassigns or ex_deletes_count):
                await db.flush()
                fresh = (
                    await db.execute(
                        select(Exercise)
                        .where(Exercise.lesson_id == lesson.id)
                        .order_by(Exercise.order, Exercise.id)
                    )
                ).scalars().all()
                lesson.sections_json = build_sections_json(ldata, fresh)

        print(f"\n--- Summary ---")
        print(f"  Lesson field updates:    {total_lesson_fields}")
        print(f"  Exercise text updates:   {total_ex_field_updates}")
        print(f"  Exercise inserts (NEW):  {total_ex_inserts}")
        print(f"  Exercise orphans deleted:{total_ex_deletes}")

        nothing = (total_lesson_fields == 0 and total_ex_field_updates == 0
                   and total_ex_inserts == 0 and total_ex_deletes == 0)
        if nothing:
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
    parser.add_argument("--apply", action="store_true", help="Actually write changes.")
    args = parser.parse_args()
    asyncio.run(refresh(apply=args.apply))


if __name__ == "__main__":
    main()
