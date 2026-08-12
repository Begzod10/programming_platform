"""RU translation writers for the spec format — thin wrappers around
write_ru_translations.py's _write()/translate_lesson()/translate_exercises(),
which already match translation_cache's schema/hash convention exactly."""
from __future__ import annotations

import json
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson import Lesson
from app.models.exercise import Exercise

from write_ru_translations import translate_lesson, translate_exercises, _write
from course_builder.db_helpers import derive_correct_order_ru, is_natural_language_answer

# Fixed section labels build_sections_json stamps onto every lesson — these
# are genuine UZ->RU strings (label != label across languages) but constant
# regardless of lesson content, so translate_lesson()'s "every collected
# string needs a translation" check is satisfied with this static map
# rather than something the spec author has to think about per lesson.
_SECTION_LABELS_RU = {"Matn": "Текст", "Kod": "Код", "Video": "Видео", "Mashqlar": "Упражнения"}


async def translate_course_from_spec(db: AsyncSession, course, course_spec: dict) -> int:
    """Write RU translations for the course's own title/description.

    GET /courses reads these via _translate_course_dto() (courses.py) — this
    is NOT a dead/unread field the way exercise *_ru columns are. A prior
    round of course builds this session shipped 6 courses with no
    course-level RU translation at all, on the wrong assumption that no
    serving code read it; check_ru_coverage.py now flags this too, so a
    missing course_ru is a real, caught gap, not a silent one.
    Returns the number of fields written (0, 1, or 2)."""
    written = 0
    if course_spec.get("title_ru"):
        await _write(db, "course", course.id, "title", course.title, course_spec["title_ru"])
        written += 1
    if course_spec.get("description_ru"):
        await _write(db, "course", course.id, "description", course.description, course_spec["description_ru"])
        written += 1
    return written


async def translate_lesson_from_spec(db: AsyncSession, lesson: Lesson, lesson_spec: dict) -> int:
    """Write RU translations for a lesson's own fields (title, text_content,
    and everything _collect_translatable_strings finds inside its
    sections_json — the fixed section labels plus the code/text/video
    content; NOT exercise text, since build_sections_json stores exercises
    as bare {"id": N} stubs with zero translatable keys — see
    translate_exercises_from_spec for how exercise text actually gets
    translated, and lesson_helpers.py::_hydrate_exercise_sections for how
    it reaches the student at request time).
    Returns the number of strings written. No-ops (returns 0) if the spec
    has no _ru content for this lesson at all — not every lesson needs RU
    on day one, but check_ru_coverage.py will flag it as a real gap once
    the course is meant to be bilingual."""
    flat_fields = {}
    if lesson_spec.get("title_ru"):
        flat_fields["title"] = lesson_spec["title_ru"]
    if lesson_spec.get("text_content_ru"):
        flat_fields["text_content"] = lesson_spec["text_content_ru"]

    if not flat_fields:
        return 0

    section_translations = dict(_SECTION_LABELS_RU)
    if lesson.text_content and lesson_spec.get("text_content_ru"):
        section_translations[lesson.text_content] = lesson_spec["text_content_ru"]
    if lesson.code_content and lesson_spec.get("code_content_ru"):
        section_translations[lesson.code_content] = lesson_spec["code_content_ru"]

    task_spec = lesson_spec.get("task")
    if task_spec:
        # apply_submission_task() must have already run (see build_course.py
        # / the documented script order) so lesson.task_* reflects task_spec
        # — otherwise these getattr() reads are stale/None and this whole
        # block silently no-ops.
        for field in ("task_title", "task_description", "task_requirements"):
            ru_field = f"{field}_ru"
            source = getattr(lesson, field, None)
            if source and task_spec.get(ru_field):
                flat_fields[field] = task_spec[ru_field]
        # The project section build_sections_json emits inside sections_json
        # embeds task_title/task_description a SECOND time (as "label"/
        # "description" of the project section) — same string value as the
        # lesson columns above, so the same source->translated entry covers
        # both occurrences since section_translations is keyed by the
        # literal source string, not by field name.
        if task_spec.get("task_title") and task_spec.get("task_title_ru"):
            section_translations[task_spec["task_title"]] = task_spec["task_title_ru"]
        if task_spec.get("task_description") and task_spec.get("task_description_ru"):
            section_translations[task_spec["task_description"]] = task_spec["task_description_ru"]

    await translate_lesson(db, lesson.id, flat_fields=flat_fields, section_translations=section_translations)
    return len(flat_fields) + len(section_translations)


async def translate_exercises_from_spec(
    db: AsyncSession, exercises: list[Exercise], exercise_specs: list[dict]
) -> int:
    """Write RU translations for every exercise in a lesson. Handles the
    options/drag_items JSON-array shape and auto-derives correct_order_ru
    via derive_correct_order_ru — the spec author only ever writes
    drag_items_ru as a parallel array, never a hand-mapped correct_order_ru.
    Returns the number of exercises that got at least one translated
    field written."""
    translations: dict[int, dict[str, str]] = {}

    for ex, spec in zip(exercises, exercise_specs):
        fields: dict[str, str] = {}

        if spec.get("title_ru"):
            fields["title"] = spec["title_ru"]
        if spec.get("description_ru"):
            fields["description"] = spec["description_ru"]
        if spec.get("hint_ru") and ex.hint:
            fields["hint"] = spec["hint_ru"]

        options_ru = spec.get("options_ru")
        if options_ru is not None:
            options = spec.get("options") or []
            if len(options_ru) != len(options):
                raise ValueError(
                    f"exercise {ex.id!r} ({spec.get('title')!r}): options_ru has "
                    f"{len(options_ru)} entries but options has {len(options)}"
                )
            fields["options"] = json.dumps(options_ru, ensure_ascii=False)

        drag_items_ru = spec.get("drag_items_ru")
        if drag_items_ru is not None:
            drag_items = spec.get("drag_items") or []
            correct_order = spec.get("correct_order") or []
            fields["drag_items"] = json.dumps(drag_items_ru, ensure_ascii=False)
            order_ru = derive_correct_order_ru(drag_items, drag_items_ru, correct_order)
            fields["correct_order"] = json.dumps(order_ru, ensure_ascii=False)

        correct_answers_ru = spec.get("correct_answers_ru")
        correct_answers = spec.get("correct_answers")
        if correct_answers_ru:
            fields["correct_answers"] = correct_answers_ru
        elif correct_answers and spec.get("exercise_type") in ("fill_in_blank", "text_input") \
                and is_natural_language_answer(correct_answers):
            raise ValueError(
                f"exercise {ex.id!r} ({spec.get('title')!r}): correct_answers "
                f"{correct_answers!r} looks like natural language but no "
                f"correct_answers_ru was given — either add a grammatically "
                f"correct RU translation, or if it's actually a technical "
                f"token, that's fine, just confirms nothing needed here"
            )

        if fields:
            translations[ex.id] = fields

    if translations:
        await translate_exercises(db, translations)
    return len(translations)
