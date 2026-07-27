"""DB-writing mechanism shared by every course-building script. Pure
mechanism — no course content lives here. See course_builder/__init__.py
for the spec module contract these functions expect."""
from __future__ import annotations

import json
import re
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.lesson import Lesson
from app.models.exercise import Exercise
from app.models.lesson_sample import LessonSample

_VALID_DIFFICULTY = {"Easy", "Medium", "Hard"}
_VALID_EXERCISE_TYPES = {"fill_in_blank", "drag_and_drop", "multiple_choice", "text_input"}

_CODE_LIKE_PATTERN = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_.]*$"
    r"|^[A-Za-z0-9_\-]+\(.*\)$"
    r"|[<>{}();=]"
)


def is_natural_language_answer(answer: Optional[str]) -> bool:
    """True if `answer` looks like a real word/phrase worth a RU
    translation, False if it looks like a code/technical token that must
    stay literal in every language. Same heuristic check_ru_coverage.py
    uses to decide whether a missing correct_answers translation is a real
    gap — kept here too so spec authors can call it while writing content,
    not just discover a mismatch after the fact."""
    a = (answer or "").strip()
    if not a or len(a) > 40:
        return False
    if _CODE_LIKE_PATTERN.search(a):
        return False
    if a.isupper() or a.isdigit():
        return False
    return any(c.isalpha() for c in a)


def derive_correct_order_ru(
    drag_items: list[str], drag_items_ru: list[str], correct_order: list[str]
) -> list[str]:
    """Build the RU correct_order by index-mapping — never hand-type this.

    For each entry in the UZ `correct_order`, find its index in the UZ
    `drag_items` (consuming the first not-yet-matched occurrence, so
    duplicate item text maps 1:1 in order), then take the item at that
    same index from `drag_items_ru`. This is the exact algorithm every
    translation agent this session was told to follow by hand — baking it
    into the tooling means a spec author only ever writes drag_items_ru
    (a straightforward parallel array) and never has to get the reordering
    right themselves.
    """
    if len(drag_items) != len(drag_items_ru):
        raise ValueError(
            f"drag_items has {len(drag_items)} entries but drag_items_ru has "
            f"{len(drag_items_ru)} — they must be the same length/order"
        )
    remaining = list(enumerate(drag_items))
    order_ru: list[str] = []
    for entry in correct_order:
        for pos, (idx, val) in enumerate(remaining):
            if val == entry:
                order_ru.append(drag_items_ru[idx])
                remaining.pop(pos)
                break
        else:
            raise ValueError(
                f"correct_order entry {entry!r} not found in remaining drag_items "
                f"{[v for _, v in remaining]} — correct_order must be a permutation "
                f"of drag_items"
            )
    return order_ru


def _jdump(value) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_sections_json(
    order: int,
    text: Optional[str],
    code: Optional[str],
    video: Optional[str],
    exercise_rows: list[Exercise],
    lang: str = "text",
    project_task: Optional[dict] = None,
) -> str:
    """Build a lesson's sections_json from its flat columns + live exercise
    rows.

    Exercise entries are deliberately kept as BARE stubs (just {"id": N,
    "type": "exercise"} — no title/description/options embedded) rather
    than a full snapshot. The in-lesson exercise view is what students
    actually see (confirmed: the standalone GET .../exercises?lang=
    endpoint has no frontend caller at all), and it's populated by
    _hydrate_exercise_sections in lesson_helpers.py, which is lang-aware —
    it looks up each field in translation_store (falling back to the live
    Exercise row) at REQUEST time. A bare stub can never go stale relative
    to the exercises table, and never needs a lesson-level RU
    sections_json re-sync just because an exercise's text changed — full
    embedding was the exact mechanism that let 63+ lessons platform-wide
    silently serve untranslated Uzbek exercise text to Russian students
    (a stub with no cached RU counterpart falls back to a live re-fetch,
    which historically ignored lang entirely — now fixed, but a stub
    remains strictly safer than a frozen full embed either way)."""
    sections = []
    if text:
        sections.append({"id": f"t{order}", "type": "text", "label": "Matn", "html": text, "order": 0})
    if code:
        sections.append({"id": f"c{order}", "type": "code", "label": "Kod", "code": code, "lang": lang, "order": 1})
    if video:
        sections.append({"id": f"v{order}", "type": "video", "label": "Video", "videoUrl": video, "order": 2})
    if exercise_rows:
        sections.append({
            "id": f"e{order}", "type": "exercise", "label": "Mashqlar",
            "exercises": [{"id": e.id} for e in exercise_rows],
            "order": 3,
        })
    if project_task:
        sections.append({
            "id": f"p{order}", "type": "project", "label": project_task.get("task_title", "Loyiha"),
            "description": project_task.get("task_description", ""),
            "requirements": project_task.get("task_requirements", ""),
            "techStack": project_task.get("task_technologies", ""),
            "deadline": project_task.get("task_deadline_days"),
            "order": 4,
        })
    return json.dumps(sections, ensure_ascii=False)


async def get_or_create_course(db: AsyncSession, course_spec: dict) -> tuple[Course, bool]:
    """Returns (course, created). Idempotent by title — re-running with
    the same COURSE dict never creates a duplicate."""
    existing = (
        await db.execute(select(Course).where(Course.title == course_spec["title"]))
    ).scalar_one_or_none()
    if existing:
        return existing, False

    course = Course(
        title=course_spec["title"],
        description=course_spec["description"],
        instructor_id=course_spec["instructor_id"],
        difficulty_level=course_spec["difficulty_level"],
        duration_weeks=course_spec["duration_weeks"],
        max_points=course_spec["max_points"],
        category_id=course_spec.get("category_id"),
        prerequisite_course_id=course_spec.get("prerequisite_course_id"),
        display_order=course_spec.get("display_order", 0),
        image_url=course_spec.get("image_url"),
        thumbnail_url=course_spec.get("thumbnail_url"),
        is_active=course_spec.get("is_active", True),
        is_published=course_spec.get("is_published", False),
    )
    db.add(course)
    await db.flush()
    return course, True


async def get_or_create_lesson(db: AsyncSession, course_id: int, lesson_spec: dict) -> tuple[Lesson, bool]:
    """Returns (lesson, created). Idempotent by (course_id, order)."""
    existing = (
        await db.execute(
            select(Lesson).where(Lesson.course_id == course_id, Lesson.order == lesson_spec["order"])
        )
    ).scalar_one_or_none()
    if existing:
        return existing, False

    lesson = Lesson(
        course_id=course_id,
        title=lesson_spec["title"],
        order=lesson_spec["order"],
        points_reward=lesson_spec.get("points_reward", 10),
        text_content=lesson_spec.get("text_content"),
        code_content=lesson_spec.get("code_content"),
        code_language=lesson_spec.get("code_language"),
        video_url=lesson_spec.get("video_url"),
        is_active=True,
        is_published=True,
    )
    db.add(lesson)
    await db.flush()
    return lesson, True


async def sync_lesson_exercises(db: AsyncSession, lesson: Lesson, exercise_specs: list[dict]) -> list[Exercise]:
    """Create exercise rows for a lesson and rebuild its sections_json
    exercise section. Idempotent: if the lesson already has exercises,
    returns them unchanged rather than creating duplicates on a re-run —
    delete the existing rows first if you genuinely want to replace them."""
    existing = (
        await db.execute(select(Exercise).where(Exercise.lesson_id == lesson.id).order_by(Exercise.order))
    ).scalars().all()
    if existing:
        return list(existing)

    rows: list[Exercise] = []
    for i, spec in enumerate(exercise_specs):
        ex_type = spec["exercise_type"]
        if ex_type not in _VALID_EXERCISE_TYPES:
            raise ValueError(f"lesson {lesson.id} exercise {i}: invalid exercise_type {ex_type!r}")
        difficulty = spec.get("difficulty_level", "Medium")
        if difficulty not in _VALID_DIFFICULTY:
            raise ValueError(f"lesson {lesson.id} exercise {i}: invalid difficulty_level {difficulty!r}")

        row = Exercise(
            lesson_id=lesson.id,
            title=spec["title"],
            description=spec["description"],
            exercise_type=ex_type,
            options=_jdump(spec.get("options")),
            correct_answers=spec.get("correct_answers") or "",
            drag_items=_jdump(spec.get("drag_items")),
            correct_order=_jdump(spec.get("correct_order")),
            is_multiple_select=bool(spec.get("is_multiple_select", False)),
            expected_answer=spec.get("expected_answer") or "",
            hint=spec.get("hint") or "",
            explanation=spec.get("explanation") or "",
            difficulty_level=difficulty,
            points=spec.get("points", 10),
            order=i,
            is_active=True,
        )
        db.add(row)
        rows.append(row)
    await db.flush()

    lesson.sections_json = build_sections_json(
        lesson.order, lesson.text_content, lesson.code_content, lesson.video_url,
        rows, lang=lesson.code_language or "text",
    )
    return rows


async def sync_lesson_sample(db: AsyncSession, lesson_id: int, sample_spec: Optional[dict]) -> Optional[LessonSample]:
    """Create the lesson's namuna row. Idempotent: no-ops if one already
    exists (LessonSample.lesson_id is unique, so a second insert would
    fail anyway — this just makes the no-op explicit and safe)."""
    if not sample_spec:
        return None
    existing = (
        await db.execute(select(LessonSample).where(LessonSample.lesson_id == lesson_id))
    ).scalar_one_or_none()
    if existing:
        return existing

    sample = LessonSample(
        lesson_id=lesson_id,
        title=sample_spec["title"],
        description=sample_spec.get("description"),
        sample_type=sample_spec.get("sample_type", "code"),
        html_code=sample_spec.get("html_code"),
        css_code=sample_spec.get("css_code"),
        js_code=sample_spec.get("js_code"),
        code_files_json=_jdump(sample_spec.get("code_files")) or None,
    )
    db.add(sample)
    await db.flush()
    return sample


async def apply_submission_task(db: AsyncSession, lesson: Lesson, task_spec: Optional[dict]) -> bool:
    """UPDATE the lesson's task_* columns from the spec. Not an insert —
    the lesson row must already exist. Returns True if anything was set.
    Safe to re-run: setting the same values twice is a no-op in effect."""
    if not task_spec:
        return False

    lesson.task_title = task_spec.get("task_title")
    lesson.task_description = task_spec.get("task_description")
    lesson.task_requirements = task_spec.get("task_requirements")
    lesson.task_technologies = task_spec.get("task_technologies")
    lesson.task_deadline_days = task_spec.get("task_deadline_days")

    # task fields changed → the embedded sections_json "project" section
    # must be rebuilt too, or the lesson page's project section stays
    # stale/absent even though the DB columns are now populated.
    existing_ex = (
        await db.execute(select(Exercise).where(Exercise.lesson_id == lesson.id).order_by(Exercise.order))
    ).scalars().all()
    lesson.sections_json = build_sections_json(
        lesson.order, lesson.text_content, lesson.code_content, lesson.video_url,
        list(existing_ex), lang=lesson.code_language or "text", project_task=task_spec,
    )
    return True
