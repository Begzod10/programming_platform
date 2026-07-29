"""Report Mermaid diagram coverage for one or more courses.

Why this exists: course 109 ("SQL + Python ORM va Migratsiyalar") was built
in full — content, exercises, tasks, samples, RU translation — with zero
visual diagrams, even on lessons (ORM relationships, migration before/after
schemas) where a diagram is the obvious, standard way to teach the concept.
Nothing in the pipeline caught this because diagrams aren't a schema field
that can be "missing" — they're an authoring convention (a
`<pre class="mermaid">...</pre>` block inside a lesson's text_content) that
is trivially easy to just never think to include.

This check is INFORMATIONAL ONLY — it never fails the build and is not a
"problem" the way check_ru_coverage/check_exercise_integrity are. Whether a
given lesson NEEDS a diagram is a pedagogical judgment call (see
course_builder/__init__.py's "Diagrams (Mermaid)" section), not something
this script can decide. Its only job is to make the omission VISIBLE at
build time, so "we forgot diagrams entirely" is a choice a human/agent
consciously makes, not a silent gap discovered later from a user screenshot.

Usage:
    cd backend
    python scripts/check_diagram_coverage.py <course_id> [<course_id> ...]
    python scripts/check_diagram_coverage.py --all

Always exits 0 — informational only.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.db import base as _base  # noqa: E402,F401 ensure all models registered
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402

_MERMAID_MARKER = 'class="mermaid"'


async def diagram_coverage(db, course_id: int) -> str:
    """Returns a one-line human-readable coverage summary for the course.
    Never raises for a course with zero diagrams — that may be the right
    call for a course whose content genuinely has nothing worth diagramming
    (e.g. a syntax-drills course) — this just makes the number visible."""
    course = (await db.execute(select(Course).where(Course.id == course_id))).scalar_one_or_none()
    if not course:
        return f"course {course_id}: does not exist"

    lessons = (await db.execute(
        select(Lesson).where(Lesson.course_id == course_id)
    )).scalars().all()
    if not lessons:
        return f"course {course_id} ({course.title!r}): has no lessons"

    with_diagram = [l for l in lessons if l.text_content and _MERMAID_MARKER in l.text_content]
    without = [l for l in lessons if l not in with_diagram]

    if not with_diagram:
        return (
            f"course {course_id} ({course.title!r}): 0/{len(lessons)} lessons have a diagram — "
            f"if any lesson teaches a schema, relationship, decomposition, or multi-step "
            f"flow, consider adding a Mermaid diagram (see course_builder/__init__.py)"
        )
    return (
        f"course {course_id} ({course.title!r}): {len(with_diagram)}/{len(lessons)} lessons have a "
        f"diagram — lessons without one: {[l.id for l in without]}"
    )


async def main(course_ids: list[int] | None) -> int:
    async with AsyncSessionLocal() as db:
        if course_ids is None:
            rows = (await db.execute(select(Course.id))).scalars().all()
            course_ids = list(rows)

        for cid in course_ids:
            print(await diagram_coverage(db, cid))

    await engine.dispose()
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    ids = None if args == ["--all"] else [int(a) for a in args]
    sys.exit(asyncio.run(main(ids)))
