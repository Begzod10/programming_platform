"""Apply targeted corrections to existing lesson_questions rows.

Companion to insert_lesson_bug_questions_batch.py, but for UPDATEs instead of
inserts — used to fix audit-flagged issues (wrong correct_option, topically
mismatched question content, mislabeled bug_line/code_language) without
touching any row that wasn't explicitly flagged.

Input JSON shape:
{
  "fixes": [
    {"id": 1821, "fields": {"correct_option": 1}},
    {"id": 3007, "fields": {"question_text": "...", "options": ["a","b","c","d"], "correct_option": 0}},
    ...
  ]
}

Only the keys present in "fields" are touched — every other column on the
row is left alone. Prints a before/after diff per row so the change is
auditable from the run log, then commits once at the end.

Usage: python3 scripts/apply_lesson_question_fixes.py <path-to-json> [--dry-run]
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

ALLOWED_FIELDS = {
    "question_text", "options", "correct_option", "time_limit", "points",
    "code_snippet", "code_language", "bug_line", "distractor_lines",
    "bug_explanation", "bug_explanation_ru",
}


async def main(path: str, dry_run: bool) -> None:
    data = json.load(open(path, encoding="utf-8"))
    fixes = data["fixes"]

    async with AsyncSessionLocal() as db:
        updated = 0
        skipped = 0
        for fix in fixes:
            qid = fix["id"]
            fields = fix["fields"]
            bad_keys = set(fields) - ALLOWED_FIELDS
            if bad_keys:
                raise ValueError(f"id={qid}: unknown fields {bad_keys}")

            row = (await db.execute(
                select(LessonQuestion).where(LessonQuestion.id == qid)
            )).scalar_one_or_none()
            if row is None:
                print(f"SKIP id={qid}: no such lesson_question")
                skipped += 1
                continue

            diffs = []
            for key, new_val in fields.items():
                old_val = getattr(row, key)
                if old_val != new_val:
                    diffs.append((key, old_val, new_val))
                    if not dry_run:
                        setattr(row, key, new_val)

            if not diffs:
                print(f"NOCHANGE id={qid} (lesson {row.lesson_id}): fields already match")
                continue

            print(f"{'DRYRUN' if dry_run else 'UPDATE'} id={qid} (lesson {row.lesson_id}, {row.question_kind}):")
            for key, old_val, new_val in diffs:
                print(f"  {key}: {old_val!r}  ->  {new_val!r}")
            updated += 1

        if not dry_run:
            await db.commit()
        print(f"\n{'Would update' if dry_run else 'Updated'} {updated} row(s), skipped {skipped} not-found id(s).")


if __name__ == "__main__":
    path = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    asyncio.run(main(path, dry_run))
