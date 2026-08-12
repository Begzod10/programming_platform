"""Fix drag-and-drop exercise 3364 (course 55 "SASS/SCSS Asoslari", lesson
510 "Mixins va @include"): two of the five draggable chips were both a bare
'}' (one originally indented as '  }', one not). The frontend strips
indentation before rendering drag chips, so students saw two visually
identical pills and couldn't tell which closing brace belonged where.

Fix: make every chip textually distinct by annotating the two closing
braces with an inline comment naming what they close, while preserving the
exact same nesting logic being tested. Also updates this exercise's entry
inside lesson 510's sections_json (which embeds a denormalized copy).
"""
from __future__ import annotations
import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.exercise import Exercise  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402

EXERCISE_ID = 3364
LESSON_ID = 510

NEW_CORRECT_ORDER = [
    "@mixin mobile {",
    "  @media (max-width: 640px) {",
    "    @content;",
    "  } // @media yopiladi",
    "} // @mixin yopiladi",
]

# Shuffled presentation order (kept distinct from correct order, same as before).
NEW_DRAG_ITEMS = [
    "  @media (max-width: 640px) {",
    "@mixin mobile {",
    "    @content;",
    "} // @mixin yopiladi",
    "  } // @media yopiladi",
]


async def main():
    async with AsyncSessionLocal() as db:
        ex = (await db.execute(select(Exercise).where(Exercise.id == EXERCISE_ID))).scalar_one()
        ex.drag_items = json.dumps(NEW_DRAG_ITEMS, ensure_ascii=False)
        ex.correct_order = json.dumps(NEW_CORRECT_ORDER, ensure_ascii=False)

        lesson = (await db.execute(select(Lesson).where(Lesson.id == LESSON_ID))).scalar_one()
        tree = json.loads(lesson.sections_json)
        for section in tree:
            if section["type"] != "exercise":
                continue
            for e in section["exercises"]:
                if e.get("id") == EXERCISE_ID:
                    e["drag_items"] = NEW_DRAG_ITEMS
                    e["correct_order"] = NEW_CORRECT_ORDER
        lesson.sections_json = json.dumps(tree, ensure_ascii=False)

        await db.commit()
        print(f"Exercise {EXERCISE_ID}: drag_items/correct_order fixed "
              f"(closing braces now distinct), lesson {LESSON_ID} sections_json updated")


if __name__ == "__main__":
    asyncio.run(main())
