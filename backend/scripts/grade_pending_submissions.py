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
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, ".")

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db import base as _b  # noqa: F401 — registers mappers
from app.models.project import Project
from app.models.submission import Submission
from app.models.user import Student
from app.config import settings

PROJECTS_UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "projects"


def _zip_is_empty(project_files: str) -> bool:
    """Return True if the ZIP file is missing, unreadable, or contains no files."""
    try:
        zip_path = PROJECTS_UPLOAD_DIR / Path(project_files).name
        if not zip_path.exists():
            return True
        with zipfile.ZipFile(zip_path, "r") as zf:
            entries = [e for e in zf.namelist() if not e.endswith("/")]
            return len(entries) == 0
    except Exception:
        return True


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
    """Pending submissions with a GitHub URL or uploaded ZIP that have not
    been reviewed yet (reviewed_at IS NULL)."""
    from sqlalchemy import or_
    stmt = (
        select(Project)
        .where(Project.status == "Submitted")
        .where(Project.reviewed_at.is_(None))
        .where(
            or_(
                Project.github_url.is_not(None),
                Project.project_files.is_not(None),
            )
        )
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
            src = p.github_url or p.project_files or "(no source)"
            empty_flag = " [EMPTY ZIP]" if (p.project_files and not p.github_url and _zip_is_empty(p.project_files)) else ""
            tag = f"#{p.id:>5} student={p.student_id} src={src[:60]}{empty_flag}"
            print(f"  - {tag}")

        if not args.apply:
            print("\n-- DRY RUN — pass --apply to actually grade them --")
            return

        # Import lazily so the dry-run path doesn't pay for the AI client.
        from app.services.ai_review_service import run_ai_review_for_project

        rejected = 0
        graded = 0
        for p in candidates:
            # Auto-reject empty ZIP submissions before AI grading
            if p.project_files and not p.github_url and _zip_is_empty(p.project_files):
                p.status = "Rejected"
                p.instructor_feedback = "ZIP fayl bo'sh yoki o'qib bo'lmaydi. Iltimos, loyihangizni qayta yuboring."
                p.reviewed_at = datetime.now(timezone.utc)
                await db.commit()
                rejected += 1
                print(f"   ✗ rejected (empty ZIP): project #{p.id} student={p.student_id}")
                continue

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

        print(f"\nDone. Rejected {rejected} empty ZIP(s). Graded {graded} / {len(candidates) - rejected} project(s).")


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
