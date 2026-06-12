"""
grade_pending_submissions.py
============================

Run the AI grader on Projects that are stuck at status="Submitted" and
have never been graded (reviewed_at IS NULL). Useful for backfilling the
window where GitHub-URL lesson submissions weren't auto-reviewed because
the lesson submit endpoint didn't trigger the AI pipeline.

Usage:
    cd /var/www/tech_gennis/backend && source venv/bin/activate
    python -m scripts.grade_pending_submissions                       # dry-run list
    python -m scripts.grade_pending_submissions --apply                # grade all pending
    python -m scripts.grade_pending_submissions --apply --student-id 12
    python -m scripts.grade_pending_submissions --apply --username Saparov_MuhammadALi
    python -m scripts.grade_pending_submissions --apply --project-id 47
    python -m scripts.grade_pending_submissions --apply --lesson-id 6 --student-id 12

The AI service handles its own commits, daily caps, and per-project
re-review block (reviewed_at IS NULL gate). Safe to re-run — already-
graded rows are filtered out at the SQL level.
"""

import argparse
import asyncio
import sys

sys.path.insert(0, ".")

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db import base as _b  # noqa: F401 — registers mappers
from app.models.project import Project
from app.models.submission import Submission
from app.models.user import Student


async def _resolve_student_id(db, username: str | None, student_id: int | None) -> int | None:
    if student_id is not None:
        return student_id
    if not username:
        return None
    row = (
        await db.execute(
            select(Student.id).where(Student.username == username)
        )
    ).scalar_one_or_none()
    if row is None:
        print(f"!  no student with username={username!r}")
    return row


async def _find_candidates(
    db,
    student_id: int | None,
    project_id: int | None,
    lesson_id: int | None,
) -> list[Project]:
    """Pending GitHub submissions only — ZIP-only entries already get AI
    via the upload endpoint, so we don't double-trigger."""
    stmt = (
        select(Project)
        .where(Project.status == "Submitted")
        .where(Project.reviewed_at.is_(None))
        .where(Project.github_url.is_not(None))
    )
    if project_id is not None:
        stmt = stmt.where(Project.id == project_id)
    if student_id is not None:
        stmt = stmt.where(Project.student_id == student_id)
    if lesson_id is not None:
        # Join via Submission to scope by lesson
        stmt = stmt.join(Submission, Submission.project_id == Project.id).where(
            Submission.lesson_id == lesson_id
        )
    return list((await db.execute(stmt)).scalars().all())


async def run(args: argparse.Namespace) -> None:
    async with AsyncSessionLocal() as db:
        sid = await _resolve_student_id(db, args.username, args.student_id)
        if (args.username or args.student_id is not None) and sid is None:
            return

        candidates = await _find_candidates(
            db,
            student_id=sid,
            project_id=args.project_id,
            lesson_id=args.lesson_id,
        )

        print(f"Found {len(candidates)} pending project(s) needing AI grading.")
        if not candidates:
            return

        for p in candidates:
            tag = f"#{p.id:>5} student={p.student_id} github={(p.github_url or '')[:60]}"
            print(f"  - {tag}")

        if not args.apply:
            print("\n-- DRY RUN — pass --apply to actually grade them --")
            return

        # Import lazily so the dry-run path doesn't pay for the AI client.
        from app.services.ai_review_service import run_ai_review_for_project

        graded = 0
        for p in candidates:
            print(f"\n→ grading project #{p.id} …")
            result = await run_ai_review_for_project(db, p, raise_on_error=False)
            if result.get("success"):
                graded += 1
                print(
                    f"   ✓ graded: grade={result.get('grade')} "
                    f"points={result.get('points')}"
                )
            else:
                print(
                    f"   ! skipped: {result.get('reason') or result.get('detail') or 'unknown'}"
                )

        print(f"\nDone. Graded {graded} / {len(candidates)} project(s).")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apply", action="store_true",
                   help="Run the grader. Without this flag, the script lists candidates only.")
    p.add_argument("--project-id", type=int, default=None,
                   help="Grade only this project id.")
    p.add_argument("--student-id", type=int, default=None,
                   help="Limit to one student's pending projects.")
    p.add_argument("--username", type=str, default=None,
                   help="Limit to one student by username (resolved to student_id).")
    p.add_argument("--lesson-id", type=int, default=None,
                   help="Limit to pending projects on one lesson.")
    args = p.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
