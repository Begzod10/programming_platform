"""Insert a batch of bug-hunt questions into lesson_questions.

Input: a JSON file matching the shape
[
  {"lesson_id": 218, "questions": [
    {"question_text": "...", "code_snippet": "...", "code_language": "python",
     "bug_line": 3, "distractor_lines": [5, 9], "bug_explanation": "...",
     "bug_explanation_ru": "..."},
    ...
  ]},
  ...
]

Mirrors the validation rules in BugQuestionCreate (app/schemas/team_game.py)
so a bad entry fails loudly here rather than reaching the live game bank.
Skips any lesson_id that already has a bug_hunt question (safe to re-run).

Usage: python3 insert_lesson_bug_questions_batch.py <path-to-json>
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.lesson_question import LessonQuestion  # noqa: E402
from app.services.points_scale import points_for_difficulty  # noqa: E402

SUPPORTED_LANGUAGES = {"javascript", "python", "html", "css"}


def validate(entry: dict) -> list[str]:
    errors = []
    lesson_id = entry.get("lesson_id")
    if not isinstance(lesson_id, int):
        errors.append(f"bad lesson_id: {lesson_id!r}")
    questions = entry.get("questions")
    if not isinstance(questions, list) or not questions:
        errors.append(f"lesson {lesson_id}: no questions list")
        return errors
    for i, q in enumerate(questions):
        tag = f"lesson {lesson_id} q{i}"
        text = q.get("question_text")
        snippet = q.get("code_snippet")
        lang = q.get("code_language")
        bug_line = q.get("bug_line")
        distractors = q.get("distractor_lines")
        explanation = q.get("bug_explanation")

        if not isinstance(text, str) or not text.strip():
            errors.append(f"{tag}: empty question_text")
        if not isinstance(snippet, str) or not snippet.strip():
            errors.append(f"{tag}: empty code_snippet")
            continue
        if lang not in SUPPORTED_LANGUAGES:
            errors.append(f"{tag}: code_language {lang!r} not in {sorted(SUPPORTED_LANGUAGES)}")
        if not isinstance(explanation, str) or not explanation.strip():
            errors.append(f"{tag}: empty bug_explanation")
        if not isinstance(bug_line, int) or bug_line < 1:
            errors.append(f"{tag}: bug_line must be an int >= 1, got {bug_line!r}")
            continue
        if not isinstance(distractors, list) or not (2 <= len(distractors) <= 5):
            errors.append(f"{tag}: distractor_lines must be a list of 2-5 ints, got {distractors!r}")
            continue
        if len(distractors) != len(set(distractors)):
            errors.append(f"{tag}: distractor_lines must not contain duplicates")
        if any(not isinstance(n, int) or n < 1 for n in distractors):
            errors.append(f"{tag}: distractor_lines must all be ints >= 1")
        if bug_line in distractors:
            errors.append(f"{tag}: bug_line must not also appear in distractor_lines")

        line_count = len(snippet.split("\n"))
        if bug_line > line_count:
            errors.append(f"{tag}: bug_line {bug_line} exceeds snippet length ({line_count} lines)")
        if any(isinstance(n, int) and n > line_count for n in distractors or []):
            errors.append(f"{tag}: distractor_lines must not exceed snippet length ({line_count} lines)")
    return errors


async def main(json_path: str) -> None:
    with open(json_path, encoding="utf-8") as f:
        batch = json.load(f)

    all_errors = []
    for entry in batch:
        all_errors.extend(validate(entry))
    if all_errors:
        print(f"VALIDATION FAILED ({len(all_errors)} errors) -- nothing inserted:")
        for e in all_errors:
            print(" -", e)
        sys.exit(1)

    async with AsyncSessionLocal() as db:
        inserted_lessons = 0
        inserted_questions = 0
        for entry in batch:
            lesson_id = entry["lesson_id"]
            lesson = (await db.execute(select(Lesson).where(Lesson.id == lesson_id))).scalar_one_or_none()
            if lesson is None:
                print(f"lesson {lesson_id}: NOT FOUND, skipping")
                continue

            existing = (await db.execute(
                select(LessonQuestion).where(
                    LessonQuestion.lesson_id == lesson_id,
                    LessonQuestion.question_kind == "bug_hunt",
                )
            )).scalars().all()
            if existing:
                print(f"lesson {lesson_id}: already has {len(existing)} bug-hunt questions, skipping")
                continue

            base_order = (await db.execute(
                select(LessonQuestion).where(LessonQuestion.lesson_id == lesson_id)
            )).scalars().all()
            next_order = len(base_order)

            course = (await db.execute(select(Course).where(Course.id == lesson.course_id))).scalar_one_or_none()
            default_points = points_for_difficulty(course.difficulty_level if course else None)

            for q in entry["questions"]:
                db.add(LessonQuestion(
                    lesson_id=lesson_id,
                    question_text=q["question_text"],
                    time_limit=q.get("time_limit", 90),
                    points=q.get("points", default_points),
                    order_index=next_order,
                    question_kind="bug_hunt",
                    code_snippet=q["code_snippet"],
                    code_language=q["code_language"],
                    bug_line=q["bug_line"],
                    distractor_lines=q["distractor_lines"],
                    bug_explanation=q["bug_explanation"],
                    bug_explanation_ru=q.get("bug_explanation_ru"),
                ))
                next_order += 1
                inserted_questions += 1
            inserted_lessons += 1
            print(f"lesson {lesson_id}: inserted {len(entry['questions'])} bug-hunt questions")

        await db.commit()
        print(f"\nDone. {inserted_lessons} lessons, {inserted_questions} bug-hunt questions inserted.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 insert_lesson_bug_questions_batch.py <path-to-json>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
