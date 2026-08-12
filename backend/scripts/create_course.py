"""Create (or find, idempotently) the Course row for a spec module.

Usage:
    cd backend
    python scripts/create_course.py course_specs/my_course.py
    python scripts/create_course.py course_specs.my_course
    # add --dry-run to preview without writing

See course_builder/__init__.py for the spec module contract.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.db import base as _base  # noqa: E402,F401 ensure all models registered

from course_builder.spec_loader import load_spec, require  # noqa: E402
from course_builder.db_helpers import get_or_create_course  # noqa: E402
from course_builder.translations import translate_course_from_spec  # noqa: E402


async def main(spec_path: str, dry_run: bool) -> int:
    module = load_spec(spec_path)
    course_spec = require(module, "COURSE")

    async with AsyncSessionLocal() as db:
        course, created = await get_or_create_course(db, course_spec)
        ru_written = await translate_course_from_spec(db, course, course_spec)
        if dry_run:
            await db.rollback()
            print(f"DRY RUN — would {'create' if created else 'reuse'} course "
                  f"{course_spec['title']!r} (id={course.id if not created else '?'}), "
                  f"RU fields: {ru_written}")
        else:
            await db.commit()
            print(f"{'Created' if created else 'Reusing existing'} course: "
                  f"id={course.id} title={course.title!r} published={course.is_published} "
                  f"(RU fields written: {ru_written})")

    await engine.dispose()
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    if not args:
        print(__doc__)
        sys.exit(2)
    sys.exit(asyncio.run(main(args[0], "--dry-run" in sys.argv)))
