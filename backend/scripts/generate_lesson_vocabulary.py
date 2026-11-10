"""One-off: build the bilingual (UZ + RU) vocabulary of every active lesson that has NO vocabulary yet.

Safe to stop and re-run: a lesson that got its words is skipped next time, a lesson whose AI call failed is retried.
A lesson with any word (teacher-written or generated) is never touched.

    python scripts/generate_lesson_vocabulary.py --dry-run --limit 5      # show what would be created, write nothing
    python scripts/generate_lesson_vocabulary.py --course 12              # one course only
    python scripts/generate_lesson_vocabulary.py                          # everything

See docs/superpowers/specs/2026-11-09-lesson-vocabulary-design.md §3.2.
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
from app.models.lesson import Lesson, LessonVocabulary  # noqa: E402
from app.services.grok_ai_client import ProviderError  # noqa: E402
from app.services.lesson_vocab_ai_service import generate_for_lesson  # noqa: E402


async def run(*, dry_run: bool, limit: Optional[int], course_ids: Optional[list] = None, sleep: float = 1.0,
              verbose: bool = False) -> dict:
    """{"lessons": lessons that got terms, "terms": terms, "skipped": too little text, "failed": AI errors}.
    `limit` caps how many lessons get terms (skipped and failed lessons do not use it up)."""
    async with AsyncSessionLocal() as db:
        q = (select(Lesson.id, Lesson.title)
             .where(Lesson.is_active.is_not(False),
                    ~select(LessonVocabulary.id).where(LessonVocabulary.lesson_id == Lesson.id).exists())
             .order_by(Lesson.course_id, Lesson.order, Lesson.id))
        if course_ids:
            q = q.where(Lesson.course_id.in_(course_ids))
        todo = (await db.execute(q)).all()

    out = {"lessons": 0, "terms": 0, "skipped": 0, "failed": 0}
    for lesson_id, title in todo:
        if limit is not None and out["lessons"] >= limit:
            break
        try:
            async with AsyncSessionLocal() as db:
                added = await generate_for_lesson(db, lesson_id, dry_run=dry_run)
        except ProviderError as e:
            out["failed"] += 1
            print(f"FAILED  lesson {lesson_id} «{title}»: {e}", flush=True)
            continue
        if not added:
            out["skipped"] += 1
            if verbose:
                print(f"skipped lesson {lesson_id} «{title}» (too little text)", flush=True)
            continue
        out["lessons"] += 1
        out["terms"] += len(added)
        print(f"{'would add' if dry_run else 'added'} {len(added):2d}  lesson {lesson_id} «{title}»", flush=True)
        if verbose or dry_run:
            for t in added:
                print(f"      {t['word']}\n        uz: {t['definition']}\n        ru: {t['definition_ru']}", flush=True)
        if sleep:
            await asyncio.sleep(sleep)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="call the AI and print the terms, write nothing")
    ap.add_argument("--limit", type=int, default=None, help="stop after this many lessons got terms")
    ap.add_argument("--course", type=int, action="append", help="only this course id (repeatable)")
    ap.add_argument("--sleep", type=float, default=1.0, help="seconds between AI calls")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    print(asyncio.run(run(dry_run=a.dry_run, limit=a.limit, course_ids=a.course, sleep=a.sleep, verbose=a.verbose)))
