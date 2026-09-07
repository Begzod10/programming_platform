"""One-off audit: find already-submitted projects whose code is (or was,
at submission time) essentially the lesson's own sample project, copied.

Context: ai_review_service.run_ai_review_for_project now rejects this on
every NEW submission (see sample_copy_check.py) — added after the fact.
This script sweeps EXISTING submissions made before that guard existed,
so already-Approved projects that slipped through can be found and
reviewed by a teacher.

Read-only: never writes to the DB. Prints a report; nothing is changed
automatically — an Approved project earned real points a real student is
now relying on (leaderboard, unlocked lessons), so reversing that is a
judgment call for a human, not something this script decides.

Usage (from backend/):
    python scripts/audit_sample_copies.py             # full sweep
    python scripts/audit_sample_copies.py --limit 20   # first 20 candidates only
    python scripts/audit_sample_copies.py --status Approved  # only Approved projects

Network cost: one GitHub/ZIP fetch per candidate project, same as a real
AI review would do. Unauthenticated GitHub API calls are capped at 60/hour
per IP (see github_repo_service.py) — set GITHUB_TOKEN in .env first if
sweeping more than a couple dozen.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Quiet the SQLAlchemy engine's per-query echo (enabled by the app's dev
# DB config) — this script prints its own per-candidate progress line and
# the SQL noise makes that unreadable across thousands of rows.
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import selectinload  # noqa: E402

from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401  (registers all models)
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.lesson_sample import LessonSample  # noqa: E402
from app.models.project import Project  # noqa: E402
from app.models.submission import Submission  # noqa: E402
from app.models.user import Student  # noqa: E402
from app.services.github_repo_service import fetch_github_snapshot, fetch_zip_snapshot  # noqa: E402
from app.services.sample_copy_check import check_against_sample, load_lesson_sample_code  # noqa: E402


async def _candidates(db, status_filter: str | None):
    """(Submission, Project, Student, Lesson) rows for every submission
    against a lesson that has a LessonSample with actual code."""
    query = (
        select(Submission, Project, Student, Lesson)
        .join(Project, Project.id == Submission.project_id)
        .join(Student, Student.id == Submission.student_id)
        .join(Lesson, Lesson.id == Submission.lesson_id)
        .join(LessonSample, LessonSample.lesson_id == Lesson.id)
        .where(Submission.lesson_id.is_not(None))
        .options(selectinload(Project.student))
        .order_by(Submission.id)
    )
    if status_filter:
        query = query.where(Project.status == status_filter)
    return (await db.execute(query)).all()


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None, help="stop after this many candidates")
    parser.add_argument(
        "--status", default=None,
        help="only check projects in this status (e.g. Approved). Default: all.",
    )
    args = parser.parse_args()

    async with AsyncSessionLocal() as db:
        rows = await _candidates(db, args.status)
        print(f"Found {len(rows)} submission(s) against a lesson with a sample project"
              + (f" (status={args.status})" if args.status else "") + ".\n")

        if args.limit:
            rows = rows[: args.limit]

        # Cache sample code per lesson — many submissions share a lesson.
        sample_cache: dict[int, str | None] = {}
        # Cache GitHub snapshots per repo URL — content doesn't depend on
        # which lesson it's being compared against, and the same repo URL
        # is submitted for multiple lessons often enough (842 submissions,
        # 295 unique URLs) to matter for the 60-req/hr unauthenticated cap.
        github_cache: dict[str, dict] = {}

        flagged = []
        checked = 0
        skipped_no_code = 0
        skipped_zip_unreachable = 0

        for i, (submission, project, student, lesson) in enumerate(rows, start=1):
            if lesson.id not in sample_cache:
                sample_cache[lesson.id] = await load_lesson_sample_code(db, lesson.id)
            sample_code = sample_cache[lesson.id]

            source = "github" if project.github_url else ("zip" if project.project_files else None)
            if source is None:
                skipped_no_code += 1
                continue

            print(f"[{i}/{len(rows)}] project={project.id} student={student.username!r} "
                  f"lesson={lesson.id} ({lesson.title!r}) status={project.status} "
                  f"points={project.points_earned} source={source} ...", end=" ", flush=True)

            try:
                if source == "github":
                    if project.github_url not in github_cache:
                        github_cache[project.github_url] = await fetch_github_snapshot(project.github_url)
                    snapshot = github_cache[project.github_url]
                else:
                    # project_files is a filename resolved against this
                    # PROCESS's local UPLOAD_DIR — only readable when this
                    # script runs on the actual app server. From anywhere
                    # else it will correctly (harmlessly) report "not found".
                    snapshot = fetch_zip_snapshot(project.project_files)
            except Exception as e:  # noqa: BLE001 — best-effort sweep, one bad repo shouldn't stop it
                print(f"FETCH ERROR: {e}")
                continue

            if not snapshot["exists"] or not snapshot["content_text"]:
                if source == "zip":
                    skipped_zip_unreachable += 1
                    print("ZIP not reachable from this machine, skipped")
                else:
                    skipped_no_code += 1
                    print(f"no readable code ({snapshot.get('error') or 'empty'}), skipped")
                continue

            checked += 1
            result = check_against_sample(snapshot["content_text"], sample_code)
            if result.is_copy:
                print(f"*** COPY ({result.ratio:.0%}) ***")
                flagged.append((project, student, lesson, result.ratio))
            elif result.available:
                print(f"ok ({result.ratio:.0%} similarity)")
            else:
                print("too short to judge")

        print("\n" + "=" * 70)
        print(f"Checked {checked} project(s) with readable code.")
        print(f"  {skipped_no_code} had no github_url/ZIP at all, or the fetch failed.")
        print(f"  {skipped_zip_unreachable} were ZIP uploads not reachable from this "
              f"machine (run on the app server to include these).")
        print(f"  {len(github_cache)} unique GitHub repo(s) fetched for "
              f"{sum(1 for _, p, _, _ in rows if p.github_url)} github submission(s).")
        print(f"Flagged as likely sample copies: {len(flagged)}\n")

        for project, student, lesson, ratio in flagged:
            print(
                f"  project_id={project.id}  student={student.username} "
                f"(id={student.id})  lesson_id={lesson.id} ({lesson.title!r})  "
                f"status={project.status}  points_earned={project.points_earned}  "
                f"similarity={ratio:.0%}  github_url={project.github_url or '-'}"
            )

        if flagged:
            print(
                "\nNothing was changed — this is a report only. For any Approved row "
                "above, a teacher should look at the repo directly and decide whether "
                "to re-review/revoke via the normal teacher review flow."
            )


if __name__ == "__main__":
    asyncio.run(main())
