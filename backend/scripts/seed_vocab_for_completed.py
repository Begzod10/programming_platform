"""One-off: put lesson vocabulary into the dictionaries of students who finished those lessons BEFORE finishing a
lesson started doing it automatically. Words a student already has are left as they are; safe to re-run.

    python scripts/seed_vocab_for_completed.py --dry-run     # only count what would be added
    python scripts/seed_vocab_for_completed.py --course 12
    python scripts/seed_vocab_for_completed.py

See docs/superpowers/specs/2026-11-09-lesson-vocabulary-design.md §3.5.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select  # noqa: E402

from app.db import base as _all_models  # noqa: E402,F401
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.models.lesson import Lesson, LessonCompletion, LessonVocabulary  # noqa: E402
from app.services.vocab_seed_service import plan_rows, seed_lesson_words  # noqa: E402


async def run(*, dry_run: bool, limit: Optional[int], course_ids: Optional[list] = None) -> dict:
    """{"pairs": (student, finished lesson with words) pairs looked at, "rows": dictionary rows added (or, with
    dry_run, that would be added)}. `limit` caps the pairs."""
    async with AsyncSessionLocal() as db:
        q = (select(LessonCompletion.student_id, LessonCompletion.lesson_id)
             .join(Lesson, Lesson.id == LessonCompletion.lesson_id)
             .where(select(LessonVocabulary.id).where(LessonVocabulary.lesson_id == Lesson.id).exists())
             .order_by(LessonCompletion.student_id, LessonCompletion.lesson_id))
        if course_ids:
            q = q.where(Lesson.course_id.in_(course_ids))
        if limit is not None:
            q = q.limit(limit)
        pairs = (await db.execute(q)).all()

    out = {"pairs": len(pairs), "rows": 0}
    planned: dict = {}        # dry run: student_id -> (word, lang) already counted for an earlier lesson
    for i, (student_id, lesson_id) in enumerate(pairs, 1):
        async with AsyncSessionLocal() as db:
            if dry_run:
                seen = planned.setdefault(student_id, set())
                keys = {(r.word.lower(), r.lang) for r in await plan_rows(db, student_id, lesson_id)} - seen
                seen |= keys
                out["rows"] += len(keys)
            else:
                out["rows"] += await seed_lesson_words(db, student_id, lesson_id)
        if i % 500 == 0:
            print(f"{i}/{len(pairs)} pairs, {out['rows']} rows", flush=True)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="count only, write nothing")
    ap.add_argument("--limit", type=int, default=None, help="look at no more than this many pairs")
    ap.add_argument("--course", type=int, action="append", help="only this course id (repeatable)")
    a = ap.parse_args()
    print(asyncio.run(run(dry_run=a.dry_run, limit=a.limit, course_ids=a.course)))
