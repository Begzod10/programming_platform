"""Verify exercise answer-key integrity for one or more courses.

Why this exists: a platform-wide exercise audit this session found 65
exercises across multiple courses with structural answer-key bugs — not
translation gaps, actual data corruption that made the exercise unsolvable
or trivially wrong regardless of what the student picked/typed/dragged:

  - correct_order stored as integer indices instead of the drag-item text
    (backend's _norm() returns "" for non-strings, so it could never match).
  - multiple_choice correct_answers stored as a literal JSON string
    (e.g. '["A","B"]') instead of the expected comma-separated "A,B".
  - double-JSON-encoded options/drag_items — garbled text with stray
    `["`/`"]` fragments, sometimes splitting one option across two chips.
  - drag_and_drop where correct_order and drag_items have different
    lengths after the frontend's blank-chip filtering (parseListField
    drops blank entries via .filter(Boolean), but correct_order didn't
    account for that) — unconditionally wrong regardless of the answer.
  - multiple_choice correct_answers referencing a letter beyond the
    options list (e.g. "E" with only 4 options).

This is a UZ-only check — run it BEFORE translate_exercises_ru.py in the
course-building pipeline. There is no point translating an exercise whose
answer key is already broken; fix it first, then translate.

This does NOT catch semantic/content bugs (a technically well-formed
answer key that's factually wrong, e.g. correct_answers="A" when B is
actually correct) — that requires reading the exercise's technical content
and reasoning about it, which is a job for a human or an agent, not a
mechanical script. A clean report here means "structurally sound", not
"pedagogically correct".

Usage:
    cd backend
    python scripts/check_exercise_integrity.py <course_id> [<course_id> ...]
    python scripts/check_exercise_integrity.py --all

Exit code 0 = no structural problems found, 1 = problems found.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.db import base as _base  # noqa: E402,F401 ensure all models registered
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402

_VALID_TYPES = {"fill_in_blank", "drag_and_drop", "multiple_choice", "text_input"}


def _try_json_list(raw: str, label: str, problems: list[str], ex_id: int) -> list | None:
    """Parse `raw` as a JSON array; report a problem and return None on failure."""
    try:
        val = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        problems.append(f"exercise {ex_id}: {label} is not valid JSON: {raw!r:.100}")
        return None
    if not isinstance(val, list):
        problems.append(f"exercise {ex_id}: {label} parses but is not a JSON array (got {type(val).__name__})")
        return None
    if not all(isinstance(x, str) for x in val):
        problems.append(f"exercise {ex_id}: {label} contains non-string elements — "
                         f"likely double-JSON-encoded or index-based instead of text-based")
    # Detect the double-encoding symptom: a stray literal '["' / '"]' inside
    # an element means an earlier split-then-requote pass corrupted it.
    for item in val:
        if isinstance(item, str) and (item.startswith('["') or item.endswith('"]') or '", "' in item):
            problems.append(f"exercise {ex_id}: {label} element looks double-JSON-encoded: {item!r:.100}")
            break
    return val


def check_exercise(ex: Exercise) -> list[str]:
    problems: list[str] = []
    ex_id = ex.id

    if ex.exercise_type not in _VALID_TYPES:
        problems.append(f"exercise {ex_id}: unknown exercise_type {ex.exercise_type!r}")
        return problems

    if not (ex.title or "").strip():
        problems.append(f"exercise {ex_id}: empty title")
    if not (ex.description or "").strip():
        problems.append(f"exercise {ex_id}: empty description")

    if ex.exercise_type == "multiple_choice":
        if not ex.options:
            problems.append(f"exercise {ex_id}: multiple_choice with no options")
            return problems
        options = _try_json_list(ex.options, "options", problems, ex_id)
        if options is None:
            return problems
        if len(options) < 2:
            problems.append(f"exercise {ex_id}: multiple_choice has fewer than 2 options ({len(options)})")

        answers_raw = (ex.correct_answers or "").strip()
        if not answers_raw:
            problems.append(f"exercise {ex_id}: multiple_choice with empty correct_answers")
        elif answers_raw.startswith("["):
            problems.append(
                f"exercise {ex_id}: correct_answers looks like a JSON-string ({answers_raw!r:.60}) "
                f"instead of comma-separated letters (e.g. \"A,B\") — grading compares letters directly"
            )
        else:
            letters = [a.strip().upper() for a in answers_raw.split(",") if a.strip()]
            max_letter = chr(ord("A") + len(options) - 1) if options else "A"
            for letter in letters:
                if len(letter) != 1 or not letter.isalpha() or letter > max_letter:
                    problems.append(
                        f"exercise {ex_id}: correct_answers letter {letter!r} does not map to any "
                        f"of the {len(options)} options (valid range A-{max_letter})"
                    )
            if bool(ex.is_multiple_select) != (len(letters) > 1):
                problems.append(
                    f"exercise {ex_id}: is_multiple_select={ex.is_multiple_select} but "
                    f"correct_answers has {len(letters)} letter(s) ({answers_raw!r}) — "
                    f"flag/answer-count mismatch"
                )

    elif ex.exercise_type == "drag_and_drop":
        if not ex.drag_items:
            problems.append(f"exercise {ex_id}: drag_and_drop with no drag_items")
            return problems
        drag_items = _try_json_list(ex.drag_items, "drag_items", problems, ex_id)
        if not ex.correct_order:
            problems.append(f"exercise {ex_id}: drag_and_drop with no correct_order")
            return problems
        correct_order = _try_json_list(ex.correct_order, "correct_order", problems, ex_id)
        if drag_items is None or correct_order is None:
            return problems

        if len(drag_items) != len(correct_order):
            problems.append(
                f"exercise {ex_id}: drag_items has {len(drag_items)} item(s) but correct_order "
                f"has {len(correct_order)} — grading requires equal length after the frontend's "
                f"blank-chip filtering (parseListField drops empty entries); this exercise is "
                f"UNCONDITIONALLY WRONG regardless of what the student drags"
            )
        elif sorted(drag_items) != sorted(correct_order):
            problems.append(
                f"exercise {ex_id}: correct_order is not a permutation of drag_items — "
                f"contains item(s) not present in drag_items (likely stored as indices, "
                f"or edited independently and now out of sync)"
            )

        blanks = [i for i, item in enumerate(drag_items) if isinstance(item, str) and not item.strip()]
        if blanks:
            problems.append(
                f"exercise {ex_id}: drag_items has blank/whitespace-only entries at index "
                f"{blanks} — the frontend filters these out on render, so correct_order (which "
                f"still expects them) can never match"
            )

    elif ex.exercise_type == "fill_in_blank":
        if not (ex.correct_answers or "").strip():
            problems.append(f"exercise {ex_id}: fill_in_blank with empty correct_answers")
        if "___" not in (ex.description or "") and "__" not in (ex.description or ""):
            problems.append(
                f"exercise {ex_id}: fill_in_blank description has no visible blank marker "
                f"(___) — student has no cue where to type the answer"
            )

    elif ex.exercise_type == "text_input":
        # text_input is typically AI-graded (expected_answer is a rubric hint,
        # not a strict-match key) — only flag the case that actually breaks
        # local grading: a non-empty correct_answers on a type that never
        # routes through check_answer_locally's fill_in_blank branch.
        pass

    return problems


async def check_course(db, course_id: int) -> list[str]:
    course = (await db.execute(select(Course).where(Course.id == course_id))).scalar_one_or_none()
    if not course:
        return [f"course {course_id}: does not exist"]

    lessons = (await db.execute(select(Lesson.id).where(Lesson.course_id == course_id))).scalars().all()
    if not lessons:
        return [f"course {course_id} ({course.title!r}): has no lessons"]

    exercises = (await db.execute(
        select(Exercise).where(Exercise.lesson_id.in_(lessons), Exercise.is_active == True)
    )).scalars().all()

    problems: list[str] = []
    for ex in exercises:
        problems.extend(check_exercise(ex))
    return problems


async def main(course_ids: list[int] | None) -> int:
    async with AsyncSessionLocal() as db:
        if course_ids is None:
            course_ids = list((await db.execute(select(Course.id))).scalars().all())

        any_problems = False
        for cid in course_ids:
            problems = await check_course(db, cid)
            course = (await db.execute(select(Course).where(Course.id == cid))).scalar_one_or_none()
            title = course.title if course else "?"
            if problems:
                any_problems = True
                print(f"\n=== course {cid} ({title!r}): {len(problems)} problem(s) ===")
                for p in problems:
                    print(p)
            else:
                print(f"course {cid} ({title!r}): OK — no structural exercise problems")

    await engine.dispose()
    return 1 if any_problems else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    ids = None if args == ["--all"] else [int(a) for a in args]
    sys.exit(asyncio.run(main(ids)))
