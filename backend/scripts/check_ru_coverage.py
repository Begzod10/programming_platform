"""Verify RU translation coverage for one or more courses.

Why this exists: a platform-wide audit found 1,371 exercises across 21
courses whose lesson content had been translated to Russian but whose
exercises never were — students got a fully-Uzbek exercise under Russian
UI chrome. That gap only happened because course-building scripts called
translate_lesson() without also calling translate_exercises() for every
exercise, and nothing caught the omission until a student saw it. Run this
script after seeding+translating ANY new course (or after enhancing an
existing one) to catch that class of gap immediately instead of silently.

This checks EXACTLY what the live serving code reads — not what "seems
like" it should be translated:
  - Course fields: title, description — read by GET /courses via
    _translate_course_dto() (app/api/v1/endpoints/courses.py). This gap was
    found live: 6 courses built in one session had no course-level RU
    translation at all, because course_builder's own contract wrongly
    assumed (until corrected) that no serving code ever read a course-level
    translation — it does, so this is a required, not optional, field.
  - Lesson fields: title, text_content, and every string
    _collect_translatable_strings() finds inside sections_json (mirrors
    write_ru_translations.py::translate_lesson()).
  - Exercise fields: title, description, hint (only if the source is
    non-empty), options (if type has options), drag_items + correct_order
    (if drag_and_drop) — the exact field list app/api/v1/endpoints/
    exercises.py::_translate_exercise_dto() reads. NOT explanation/
    expected_answer/correct_answers — those are never read by that
    function, so their absence is not a gap (see exceptions below).
  - Exception: fill_in_blank/text_input `correct_answers` — only flagged
    as missing if the source answer is judged non-technical (see
    _looks_like_natural_language_answer), since grading only benefits from
    translating natural-language answers (see exercise_service.py::
    check_answer_locally's translation_store lookup for correct_answers /
    correct_order). This a heuristic, not authoritative — a clean report
    does not guarantee every correct_answers decision was right, only that
    nothing obviously natural-language was skipped.

Also warns (does not fail) if any exercise row has a non-empty *_ru column
(title_ru/description_ru/hint_ru/explanation_ru/expected_answer_ru) — those
columns are dead, unread by any serving code; a value there almost always
means someone translated to the wrong place.

Usage:
    cd backend
    python scripts/check_ru_coverage.py <course_id> [<course_id> ...]
    python scripts/check_ru_coverage.py --all

Exit code 0 = fully covered (or nothing to translate), 1 = gaps found.
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.db import base as _base  # noqa: E402,F401 ensure all models registered
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.exercise import Exercise  # noqa: E402
from app.models.translation_cache import TranslationCache  # noqa: E402
from app.services.translation_service import _collect_translatable_strings  # noqa: E402

LANG = "ru"

# Same field list _translate_exercise_dto actually reads.
_EXERCISE_DISPLAY_FIELDS = ("title", "description", "hint", "options", "drag_items")

# Technical tokens that should NOT be flagged as missing correct_answers/
# correct_order translations even though they're natural-seeming strings —
# kept intentionally short and conservative; false negatives here (missing
# a real gap) are far cheaper than false positives (flagging code as prose).
_CODE_LIKE_PATTERN = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_.]*$"        # bare identifier: SELECT, useState, __init__
    r"|^[A-Za-z0-9_\-]+\(.*\)$"          # call-shaped: foo(), render_template(...)
    r"|[<>{}();=]"                       # contains code punctuation
)


def _looks_like_natural_language_answer(answer: str) -> bool:
    """True if `answer` looks like a real word/phrase worth translating,
    False if it looks like a code/technical token that must stay literal.
    Conservative — only flags fairly clear-cut natural-language cases."""
    a = (answer or "").strip()
    if not a or len(a) > 40:
        return False
    if _CODE_LIKE_PATTERN.search(a):
        return False
    if a.isupper() or a.isdigit():
        return False
    return any(c.isalpha() for c in a)


async def _load_ru_cache(db, entity_type: str, entity_ids: list[int]) -> dict:
    if not entity_ids:
        return {}
    rows = (await db.execute(
        select(TranslationCache).where(
            TranslationCache.entity_type == entity_type,
            TranslationCache.entity_id.in_(entity_ids),
            TranslationCache.lang == LANG,
        )
    )).scalars().all()
    out: dict[tuple[int, str], str] = {}
    for r in rows:
        out[(r.entity_id, r.field_name)] = r.translated_text
    return out


async def check_course(db, course_id: int) -> list[str]:
    """Returns a list of problem strings; empty list = fully covered."""
    problems: list[str] = []

    course = (await db.execute(select(Course).where(Course.id == course_id))).scalar_one_or_none()
    if not course:
        return [f"course {course_id}: does not exist"]

    course_ru = await _load_ru_cache(db, "course", [course_id])
    if (course_id, "title") not in course_ru:
        problems.append(f"course {course_id} ({course.title!r}): missing RU title "
                         f"(read by GET /courses via _translate_course_dto)")
    if course.description and course.description.strip() and (course_id, "description") not in course_ru:
        problems.append(f"course {course_id} ({course.title!r}): missing RU description")

    lessons = (await db.execute(
        select(Lesson).where(Lesson.course_id == course_id)
    )).scalars().all()
    if not lessons:
        return [f"course {course_id} ({course.title!r}): has no lessons"]

    lesson_ids = [l.id for l in lessons]
    lesson_ru = await _load_ru_cache(db, "lesson", lesson_ids)

    exercises = (await db.execute(
        select(Exercise).where(Exercise.lesson_id.in_(lesson_ids), Exercise.is_active == True)
    )).scalars().all()
    ex_by_lesson: dict[int, list[Exercise]] = {}
    for e in exercises:
        ex_by_lesson.setdefault(e.lesson_id, []).append(e)
    ex_ru = await _load_ru_cache(db, "exercise", [e.id for e in exercises])

    dead_col_hits = [
        e.id for e in exercises
        if any(getattr(e, f"{fn}_ru", None) for fn in
               ("title", "description", "hint", "explanation", "expected_answer"))
    ]
    if dead_col_hits:
        problems.append(
            f"course {course_id}: {len(dead_col_hits)} exercise(s) have a "
            f"non-empty *_ru column (dead, unread by serving code) — "
            f"ids: {dead_col_hits[:10]}{'...' if len(dead_col_hits) > 10 else ''}"
        )

    for lesson in lessons:
        has_ru_title = (lesson.id, "title") in lesson_ru
        if not has_ru_title:
            # This lesson was never translated at all — its exercises are
            # not "missing" relative to it (nothing to be consistent
            # with), so skip exercise checks for this lesson but still
            # flag the lesson itself as untranslated.
            problems.append(f"lesson {lesson.id} ({lesson.title!r}): no RU title — lesson untranslated")
            continue

        if lesson.text_content and lesson.text_content.strip() and (lesson.id, "text_content") not in lesson_ru:
            problems.append(f"lesson {lesson.id} ({lesson.title!r}): missing RU text_content")

        if lesson.sections_json:
            tree = json.loads(lesson.sections_json)
            collected: list = []
            _collect_translatable_strings(tree, collected)
            if collected and (lesson.id, "sections_json") not in lesson_ru:
                problems.append(
                    f"lesson {lesson.id} ({lesson.title!r}): sections_json has "
                    f"{len(collected)} translatable string(s) but no RU sections_json"
                )

        for ex in ex_by_lesson.get(lesson.id, []):
            missing = []
            for field in _EXERCISE_DISPLAY_FIELDS:
                source = getattr(ex, field, None)
                if not source or not str(source).strip():
                    continue
                if field == "drag_items" and ex.exercise_type != "drag_and_drop":
                    continue
                if field == "options" and not ex.options:
                    continue
                if (ex.id, field) not in ex_ru:
                    missing.append(field)

            if ex.exercise_type == "drag_and_drop" and ex.correct_order:
                if (ex.id, "drag_items") in ex_ru and (ex.id, "correct_order") not in ex_ru:
                    missing.append("correct_order (drag_items is translated but correct_order isn't — "
                                    "RU students dragging the correct order will be graded wrong)")

            if ex.exercise_type in ("fill_in_blank", "text_input") and ex.correct_answers:
                if _looks_like_natural_language_answer(ex.correct_answers) and (ex.id, "correct_answers") not in ex_ru:
                    missing.append(
                        f"correct_answers (source {ex.correct_answers!r} looks like a "
                        f"natural-language word, not a code token — verify it doesn't need translating)"
                    )

            if missing:
                problems.append(
                    f"  exercise {ex.id} (lesson {lesson.id}, {ex.exercise_type!r}, {ex.title!r}): "
                    f"missing RU {missing}"
                )

    return problems


async def main(course_ids: list[int] | None) -> int:
    async with AsyncSessionLocal() as db:
        if course_ids is None:
            rows = (await db.execute(select(Course.id))).scalars().all()
            course_ids = list(rows)

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
                print(f"course {cid} ({title!r}): OK — full RU coverage")

    await engine.dispose()
    return 1 if any_problems else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    if args == ["--all"]:
        ids = None
    else:
        ids = [int(a) for a in args]
    sys.exit(asyncio.run(main(ids)))
