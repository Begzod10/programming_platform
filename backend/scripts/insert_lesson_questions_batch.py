"""Insert a batch of team-game quiz questions into lesson_questions.

Input: a JSON file matching the shape
[
  {"lesson_id": 1201, "questions": [
    {"question_text": "...", "options": ["...", "...", "...", "..."], "correct_option": 0},
    ...
  ]},
  ...
]

Skips any lesson_id that already has questions (safe to re-run / re-feed
overlapping batches). Validates each question has 2-4 options and a
correct_option within range before inserting -- a bad entry from a
content-drafting pass should fail loudly, not corrupt the live game bank.

Usage: python3 insert_lesson_questions_batch.py <path-to-json>
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
        text = q.get("question_text")
        options = q.get("options")
        correct = q.get("correct_option")
        if not isinstance(text, str) or not text.strip():
            errors.append(f"lesson {lesson_id} q{i}: empty question_text")
        if not isinstance(options, list) or not (2 <= len(options) <= 4):
            errors.append(f"lesson {lesson_id} q{i}: options must be a list of 2-4 strings, got {options!r}")
        elif not all(isinstance(o, str) and o.strip() for o in options):
            errors.append(f"lesson {lesson_id} q{i}: options contain empty/non-string entries")
        if not isinstance(correct, int) or not (isinstance(options, list) and 0 <= correct < len(options)):
            errors.append(f"lesson {lesson_id} q{i}: correct_option {correct!r} out of range for {len(options) if isinstance(options, list) else '?'} options")
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

            existing_count = (await db.execute(
                select(LessonQuestion).where(LessonQuestion.lesson_id == lesson_id)
            )).scalars().all()
            if existing_count:
                print(f"lesson {lesson_id}: already has {len(existing_count)} questions, skipping")
                continue

            course = (await db.execute(select(Course).where(Course.id == lesson.course_id))).scalar_one_or_none()
            points = points_for_difficulty(course.difficulty_level if course else None)

            for order_index, q in enumerate(entry["questions"]):
                db.add(LessonQuestion(
                    lesson_id=lesson_id,
                    question_text=q["question_text"],
                    options=q["options"],
                    correct_option=q["correct_option"],
                    time_limit=30,
                    points=points,
                    order_index=order_index,
                ))
                inserted_questions += 1
            inserted_lessons += 1
            print(f"lesson {lesson_id}: inserted {len(entry['questions'])} questions")

        await db.commit()
        print(f"\nDone. {inserted_lessons} lessons, {inserted_questions} questions inserted.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 insert_lesson_questions_batch.py <path-to-json>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
