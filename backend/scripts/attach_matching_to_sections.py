"""Append a stub {"id": N} entry for the newly-created `matching` exercise
into each lesson's sections_json exercise section's `exercises` array.

Why this is needed: StudentCourses.js's apiToLesson() renders sections
straight from lesson.sections_json when present, and ONLY falls back to the
live-fetched exercises array when sections_json has no `type: "exercise"`
section at all (see apiToLesson, line ~55: `!sections.find(s => s.type ===
'exercise')`). Every lesson here already has an embedded exercise section,
so a bare `exercises` table INSERT is invisible to students no matter what.
The backend's _hydrate_exercise_sections (lesson_helpers.py) fills in any
stub `{"id": N}` entry with the live exercise row (+ translation) at
request time — exactly the mechanism scripts/enrich_course_lessons.py
already relies on — so a stub entry is sufficient and picks up translations
automatically.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/student_platform/backend")

from sqlalchemy import select  # noqa: E402

from app.db import base as _all_models  # noqa: E402,F401
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402

# lesson_id -> new matching exercise id (from add_matching_pilot.py run)
NEW_EXERCISE_BY_LESSON = {
    218: 7438, 219: 7439, 220: 7440, 221: 7441, 222: 7442, 223: 7443,
    224: 7444, 225: 7445, 226: 7446, 227: 7447, 228: 7448, 229: 7449,
    230: 7450, 231: 7451,
}


async def main():
    async with AsyncSessionLocal() as db:
        lessons = (
            await db.execute(select(Lesson).where(Lesson.id.in_(NEW_EXERCISE_BY_LESSON.keys())))
        ).scalars().all()
        by_id = {l.id: l for l in lessons}
        assert len(by_id) == 14, f"expected 14 lessons, found {len(by_id)}"

        for lesson_id, ex_id in NEW_EXERCISE_BY_LESSON.items():
            lesson = by_id[lesson_id]
            if not lesson.sections_json:
                raise RuntimeError(f"lesson {lesson_id} has no sections_json")
            sections = json.loads(lesson.sections_json)
            ex_sections = [s for s in sections if s.get("type") == "exercise"]
            if len(ex_sections) != 1:
                raise RuntimeError(f"lesson {lesson_id}: expected exactly 1 exercise section, found {len(ex_sections)}")
            sec = ex_sections[0]
            existing_ids = {e.get("id") for e in sec.get("exercises", [])}
            if ex_id in existing_ids:
                print(f"lesson {lesson_id}: exercise {ex_id} already present, skipping")
                continue
            sec.setdefault("exercises", []).append({"id": ex_id})
            lesson.sections_json = json.dumps(sections, ensure_ascii=False)
            print(f"lesson {lesson_id}: appended stub for exercise {ex_id} "
                  f"(section now has {len(sec['exercises'])} exercises)")

        await db.commit()


if __name__ == "__main__":
    asyncio.run(main())
