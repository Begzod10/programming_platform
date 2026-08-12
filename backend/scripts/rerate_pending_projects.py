"""Re-run AI review for projects stuck in status='Submitted' with reviewed_at
IS NULL — these never got graded because the AI provider chain was down (or,
for the create_project lesson-scoped fast path, the AI trigger never fired
at all) when the student submitted.

Safe to re-run: run_ai_review_for_project() itself blocks re-review once
reviewed_at is set, so already-graded projects are untouched.
"""
from __future__ import annotations
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402
from app.db.database import AsyncSessionLocal  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.project import Project  # noqa: E402
from app.services.ai_review_service import run_ai_review_for_project  # noqa: E402


async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(
            select(Project).where(
                Project.status == "Submitted",
                Project.reviewed_at.is_(None),
            ).order_by(Project.id)
        )
        projects = res.scalars().all()
        print(f"{len(projects)} stuck projects to re-rate\n")

        for p in projects:
            print(f"--- project {p.id} ({p.title!r}, student={p.student_id}) ---")
            try:
                result = await run_ai_review_for_project(db, p, raise_on_error=False)
            except Exception as e:
                print(f"  UNHANDLED ERROR: {e}")
                continue

            if result.get("success"):
                print(f"  OK grade={result.get('grade')} points={result.get('new_points')} "
                      f"provider={result.get('provider')}")
            else:
                print(f"  FAILED reason={result.get('reason')!r} "
                      f"http_status={result.get('http_status')}")

        print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
