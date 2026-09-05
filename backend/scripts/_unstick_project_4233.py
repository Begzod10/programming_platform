"""One-off: unstick student gennis_11362's (student_id=13) orphaned
submission for lesson 1058 (project_id=4233).

Diagnosed via investigation: the project was created via create_project()
(which immediately marks a lesson-linked, github_url project "Submitted"),
but the follow-up POST /project/{id}/submit call that actually sets
submitted_at and triggers AI review never reached the server — leaving
the project permanently at status="Submitted" with submitted_at=NULL,
un-reviewed, and (until the is_orphaned_submission fix shipped alongside
this script) un-resubmittable.

This calls the real ProjectService.submit_project() — the exact code path
that should have run originally — so submitted_at gets set, Submission
stays in sync, and the actual AI review pipeline runs and grades it, same
as any normal submission. Safe to re-run: submit_project() is a no-op if
the project has already been reviewed by the time this runs.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.db import base as _base  # noqa: E402,F401  (registers all models for the mapper registry)
from app.services.project_service import ProjectService  # noqa: E402

PROJECT_ID = 4233
STUDENT_ID = 13


async def main():
    async with AsyncSessionLocal() as db:
        service = ProjectService(db)
        project = await service.get_project(PROJECT_ID)
        if project is None:
            print(f"project {PROJECT_ID} not found — nothing to do")
            return
        if project.student_id != STUDENT_ID:
            print(f"refusing: project {PROJECT_ID} belongs to student "
                  f"{project.student_id}, not {STUDENT_ID} — check the ids")
            return
        print(f"before: status={project.status} submitted_at={project.submitted_at} "
              f"reviewed_at={project.reviewed_at} points_earned={project.points_earned}")

        result = await service.submit_project(PROJECT_ID, STUDENT_ID)

        print(f"after:  status={result.status} submitted_at={result.submitted_at} "
              f"reviewed_at={result.reviewed_at} points_earned={result.points_earned} "
              f"grade={result.grade}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
