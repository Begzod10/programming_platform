"""Dump lesson content (title, chapter, task, theory text) for every lesson
outside course_id=30 (the matching-exercise pilot, already done), grouped by
course, to JSON files under /tmp/lesson_dump/ — one file per course so the
platform-wide matching-exercise rollout can be authored course-by-course by
parallel content-writing agents without any of them touching the DB.
"""
from __future__ import annotations

import asyncio
import json
import re
import sys

sys.path.insert(0, "/home/student_platform/backend")

from sqlalchemy import select  # noqa: E402

from app.db import base as _all_models  # noqa: E402,F401
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402

TAG_RE = re.compile(r"<[^>]+>")


def strip_html(html: str) -> str:
    if not html:
        return ""
    text = TAG_RE.sub(" ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


async def main():
    async with AsyncSessionLocal() as db:
        courses = (await db.execute(select(Course).where(Course.id != 30))).scalars().all()
        courses_by_id = {c.id: c for c in courses}
        lessons = (
            await db.execute(
                select(Lesson).where(Lesson.course_id.in_(courses_by_id.keys())).order_by(Lesson.course_id, Lesson.order)
            )
        ).scalars().all()

        by_course: dict[int, list] = {}
        for l in lessons:
            theory = ""
            if l.sections_json:
                try:
                    sections = json.loads(l.sections_json)
                except Exception:
                    sections = []
                text_parts = [strip_html(s.get("html", "")) for s in sections if s.get("type") == "text"]
                theory = "\n\n".join(p for p in text_parts if p)
            by_course.setdefault(l.course_id, []).append({
                "lesson_id": l.id,
                "title": l.title,
                "chapter": l.chapter,
                "task_title": l.task_title,
                "task_description": (l.task_description or "")[:800],
                "theory": theory[:4000],
            })

        import os
        os.makedirs("/tmp/lesson_dump", exist_ok=True)
        index = []
        for cid, ldata in by_course.items():
            c = courses_by_id[cid]
            fname = f"/tmp/lesson_dump/course_{cid}.json"
            with open(fname, "w", encoding="utf-8") as f:
                json.dump({"course_id": cid, "course_title": c.title, "lessons": ldata}, f, ensure_ascii=False, indent=2)
            index.append({"course_id": cid, "course_title": c.title, "num_lessons": len(ldata), "file": fname})

        with open("/tmp/lesson_dump/_index.json", "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

        print(f"dumped {len(lessons)} lessons across {len(by_course)} courses to /tmp/lesson_dump/")


if __name__ == "__main__":
    asyncio.run(main())
