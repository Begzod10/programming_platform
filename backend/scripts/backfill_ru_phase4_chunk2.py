"""Phase 4 chunk 2: hand-translated RU sibling rows for 86 lessons whose quiz
questions currently have no Russian-detected LessonQuestion row. Covers:
  - 339, 340                       (OOP: private/static/inheritance, TODO capstone)
  - 355-368                        (beginner SQL course)
  - 411-424                        (beginner Git course)
  - 453-466                        (Telegram bot course, aiogram)
  - 863-874                        (advanced SQL: window fns, indexing, locking...)
  - 889-902                        (ORM/SQLAlchemy + Alembic migrations)
  - 918-927, 929, 931, 933         (advanced Git internals)
  - 975-977                        (GitHub Actions / CI-CD)

No translation API of any kind was used. Every question_text/options string
was hand-translated (read + understood in Uzbek, written as literal Russian
text) and is stored verbatim in backfill_ru_phase4_chunk2_data.json, keyed by
the source row's id -> {"question_text": ..., "options": [...]}.

For each source uz row we INSERT a new LessonQuestion row: same lesson_id,
same order_index, same time_limit/points/correct_option, question_kind
='quiz', question_text/options set to the RU translation. question_text_ru
is intentionally left NULL on the new row (only meaningful for bug_hunt).

Idempotent / resumable: before inserting for a lesson, re-checks (via the
same Cyrillic-detection rule as _detect_lang in team_game_questions.py)
whether that lesson already has ANY ru-detected quiz row — skips if so,
so a partial re-run never creates a second ru sibling.

ORM-only via AsyncSessionLocal; no DDL; no app.main import.
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
from app.models.lesson_question import LessonQuestion  # noqa: E402

LESSON_IDS = [
    339, 340, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368,
    411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424,
    453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466,
    863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874,
    889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900, 901, 902,
    918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 929, 931, 933,
    975, 976, 977,
]

DATA_FILE = Path(__file__).resolve().parent / "backfill_ru_phase4_chunk2_data.json"


def _detect_lang(text: str) -> str:
    return "ru" if any("Ѐ" <= c <= "ӿ" for c in text) else "uz"


def _load_translations() -> dict[int, tuple[str, list[str]]]:
    raw = json.loads(DATA_FILE.read_text())
    return {int(k): (v["question_text"], v["options"]) for k, v in raw.items()}


async def main() -> None:
    row_translations = _load_translations()

    async with AsyncSessionLocal() as db:
        inserted = 0
        skipped_lessons: list[int] = []
        for lesson_id in LESSON_IDS:
            result = await db.execute(
                select(LessonQuestion).where(
                    LessonQuestion.lesson_id == lesson_id,
                    LessonQuestion.question_kind == "quiz",
                )
            )
            lesson_qs = result.scalars().all()
            if any(_detect_lang(q.question_text) == "ru" for q in lesson_qs):
                print(f"lesson {lesson_id}: already has a ru sibling row, skipping")
                skipped_lessons.append(lesson_id)
                continue

            uz_rows = [q for q in lesson_qs if _detect_lang(q.question_text) == "uz"]
            lesson_inserted = 0
            for row in sorted(uz_rows, key=lambda r: (r.order_index, r.id)):
                tr = row_translations.get(row.id)
                if tr is None:
                    print(f"  SKIP lesson {lesson_id} row {row.id}: no translation prepared")
                    continue
                q_ru, opts_ru = tr
                if row.options is not None and len(opts_ru) != len(row.options):
                    print(f"  SKIP lesson {lesson_id} row {row.id}: option count mismatch")
                    continue
                new_row = LessonQuestion(
                    lesson_id=row.lesson_id,
                    question_text=q_ru,
                    options=opts_ru,
                    correct_option=row.correct_option,
                    time_limit=row.time_limit,
                    points=row.points,
                    order_index=row.order_index,
                    question_kind="quiz",
                )
                db.add(new_row)
                inserted += 1
                lesson_inserted += 1
            print(f"lesson {lesson_id}: inserted {lesson_inserted} ru sibling rows")

        await db.commit()
        print(
            f"Phase4 chunk2: inserted {inserted} new LessonQuestion rows across "
            f"{len(LESSON_IDS) - len(skipped_lessons)} lessons "
            f"({len(skipped_lessons)} already had ru, skipped)"
        )


if __name__ == "__main__":
    asyncio.run(main())
