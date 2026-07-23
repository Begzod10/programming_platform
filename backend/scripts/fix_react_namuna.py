"""Replace course 43's (React Asoslari) vanilla-JS namuna substitutes with
real React code.

`LessonSample.sample_type` only supported web/python/sql (iframe-executed
HTML/CSS/JS), so `generate_namuna.py` silently generated vanilla-JS lookalikes
for all 14 React lessons instead of erroring — e.g. the "Context API" lesson's
namuna was a hand-rolled pub/sub object with innerHTML templating, not
createContext/useContext/Provider. The new sample_type="code" (read-only
tabbed source viewer, no execution) lets us show the ACTUAL taught code
instead. That code already exists, hand-written, in seed_react_basics.py's
L*_CODE/R*_CODE constants (the same examples used in the lesson content
itself) — so this script reuses it rather than generating anything new.

Usage:
    python -m scripts.fix_react_namuna            # dry-run (default)
    python -m scripts.fix_react_namuna --apply     # commit changes
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401 — ensure all mappers registered
from app.models.lesson import Lesson  # noqa: E402
from app.models.lesson_sample import LessonSample  # noqa: E402
from scripts.seed_react_basics import LESSONS, _resolve_lessons  # noqa: E402

COURSE_ID = 43


async def fix(apply: bool) -> None:
    _resolve_lessons()
    code_by_order = {row["order"]: row["code"] for row in LESSONS}

    label = "APPLY" if apply else "DRY-RUN"
    print(f"=== Fix React Asoslari namuna ({label}) ===\n")

    async with AsyncSessionLocal() as db:
        lessons = (
            await db.execute(
                select(Lesson).where(Lesson.course_id == COURSE_ID).order_by(Lesson.order)
            )
        ).scalars().all()

        updated = 0
        for lesson in lessons:
            code = code_by_order.get(lesson.order)
            if code is None:
                print(f"  ⚠️  lesson_id={lesson.id} order={lesson.order} — no matching "
                      f"L*/R*_CODE constant, skipped")
                continue

            sample = (
                await db.execute(
                    select(LessonSample).where(LessonSample.lesson_id == lesson.id)
                )
            ).scalar_one_or_none()
            if sample is None:
                print(f"  ⚠️  lesson_id={lesson.id} — no LessonSample row, skipped "
                      f"(create one first)")
                continue

            files = [{"filename": "App.jsx", "language": "jsx", "code": code}]
            print(f"  📝 lesson_id={lesson.id:>4}  {lesson.title:<50}  "
                  f"code_len={len(code)}")

            if apply:
                sample.sample_type = "code"
                sample.html_code = None
                sample.css_code = None
                sample.js_code = None
                sample.code_files_json = json.dumps(files, ensure_ascii=False)
            updated += 1

        if apply:
            await db.commit()

        print(f"\n--- Summary ---\n  updated: {updated}")
        if not apply:
            print("\n(dry-run — no changes written. Re-run with --apply to commit.)")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--apply", action="store_true",
                   help="Actually write to the DB. Default is dry-run.")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(fix(apply=args.apply))
