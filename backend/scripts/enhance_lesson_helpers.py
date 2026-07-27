"""Shared helpers for enhancing existing (already-seeded) lessons in place.

Used by the enhance_course_*.py scripts to append a "bug marker" section to a
lesson's text content and to add/refresh reasoning-style exercises, while
keeping the flat columns (text_content) and the embedded sections_json blob
in sync — mirrors the sync step already done by hand in
fix_capstone_final_github_only.py.

IMPORTANT: add_exercise() below only writes the Uzbek columns. If the
lesson you're enhancing already has a Russian translation (check
translation_cache for entity_type='lesson', entity_id=lesson_id, lang='ru'),
any exercise you add here needs a matching RU translation too — see
write_ru_translations.py's module docstring for the required fields and
the correct_order index-mapping rule for drag_and_drop. Run
`python scripts/check_ru_coverage.py <course_id>` after enhancing to catch
a missed exercise translation before it ships.
"""
from __future__ import annotations

import json
from sqlalchemy import select

from app.models.lesson import Lesson
from app.models.exercise import Exercise


async def append_bug_marker(db, lesson_id: int, html_addition: str) -> None:
    """Append HTML (typically a '<h3>\U0001f41b Ataylab xato</h3>...' block) to
    the lesson's text_content column and to its sections_json 'text' section."""
    lesson = (await db.execute(select(Lesson).where(Lesson.id == lesson_id))).scalar_one()
    lesson.text_content = (lesson.text_content or "") + "\n\n" + html_addition

    if lesson.sections_json:
        tree = json.loads(lesson.sections_json)
        # Append to the LAST text section (not the first) so the gotcha reads
        # as the closing beat right before the exercises, not buried mid-lesson
        # ahead of a later code/text block — lessons can have more than one
        # "text" section (e.g. explanation ... code demo ... wrap-up text).
        for section in reversed(tree):
            if section.get("type") == "text":
                section["html"] = (section.get("html") or "") + "\n\n" + html_addition
                break
        lesson.sections_json = json.dumps(tree, ensure_ascii=False)


async def add_exercise(db, lesson_id: int, *, title: str, description: str,
                        exercise_type: str, options: str | None = None,
                        correct_answers: str | None = None,
                        expected_answer: str | None = None,
                        hint: str = "", explanation: str = "",
                        difficulty_level: str = "Medium", points: int = 3) -> Exercise:
    """Insert a new exercise row at the end of the lesson's exercise order."""
    existing = (await db.execute(
        select(Exercise).where(Exercise.lesson_id == lesson_id).order_by(Exercise.order)
    )).scalars().all()
    next_order = (existing[-1].order + 1) if existing else 0
    ex = Exercise(
        lesson_id=lesson_id, title=title, description=description,
        exercise_type=exercise_type, options=options,
        correct_answers=correct_answers, expected_answer=expected_answer,
        hint=hint, explanation=explanation, difficulty_level=difficulty_level,
        points=points, order=next_order, is_active=True,
    )
    db.add(ex)
    await db.flush()
    return ex


async def sync_exercise_section(db, lesson_id: int) -> None:
    """Rebuild the sections_json 'exercise' section's embedded exercises array
    from the live exercises table, so the two never drift apart."""
    lesson = (await db.execute(select(Lesson).where(Lesson.id == lesson_id))).scalar_one()
    if not lesson.sections_json:
        return
    rows = (await db.execute(
        select(Exercise).where(Exercise.lesson_id == lesson_id).order_by(Exercise.order)
    )).scalars().all()

    def to_dict(e: Exercise) -> dict:
        return {
            "_localId": e.id, "id": e.id, "title": e.title, "description": e.description,
            "exercise_type": e.exercise_type, "options": e.options or "",
            "correct_answers": e.correct_answers or "", "drag_items": e.drag_items or "",
            "correct_order": e.correct_order or "", "is_multiple_select": bool(e.is_multiple_select),
            "expected_answer": e.expected_answer or "", "hint": e.hint or "",
            "explanation": e.explanation or "", "difficulty_level": e.difficulty_level or "Medium",
            "points": e.points, "order": e.order,
        }

    tree = json.loads(lesson.sections_json)
    for section in tree:
        if section.get("type") == "exercise":
            section["exercises"] = [to_dict(e) for e in rows]
            break
    lesson.sections_json = json.dumps(tree, ensure_ascii=False)
