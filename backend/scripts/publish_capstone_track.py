"""Publish the capstone track: all 4 capstones plus their prerequisite courses.

Flips is_published True -> False for:
    Prereqs: 72 (React RTK/TS/Testing), 74 (Node/Express), 76 (Python Testing),
             78 (Python Algorithms), 80 (TypeScript Asoslari),
             82 (Python Django), 84 (Python Advanced)
    Capstones: 86 (TaskFlow), 88 (StudyMate), 90 (MoneyLog), 92 (IssueForge)

Deliberately excludes course 33 ("Dasturlash dunyosiga kirish") — unrelated
draft, no prerequisite/capstone relationship to this track.

Usage:
    cd backend
    python -m scripts.publish_capstone_track
    # add --dry-run to preview without writing
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.course import Course  # noqa: E402

PREREQ_IDS = [72, 74, 76, 78, 80, 82, 84]
CAPSTONE_IDS = [86, 88, 90, 92]


async def run(dry_run: bool = False) -> None:
    async with AsyncSessionLocal() as db:
        for course_id in PREREQ_IDS + CAPSTONE_IDS:
            course = (
                await db.execute(select(Course).where(Course.id == course_id))
            ).scalar_one()
            was = course.is_published
            course.is_published = True
            kind = "capstone" if course_id in CAPSTONE_IDS else "prereq"
            print(f"[{kind}] {course_id}: '{course.title}'  "
                  f"is_published {was} -> True")

        if dry_run:
            await db.rollback()
            print("\nDRY RUN — rolled back, nothing written.")
        else:
            await db.commit()
            print(f"\nPublished {len(PREREQ_IDS) + len(CAPSTONE_IDS)} course(s).")


if __name__ == "__main__":
    asyncio.run(run(dry_run="--dry-run" in sys.argv))
