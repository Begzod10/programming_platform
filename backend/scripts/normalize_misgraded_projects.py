"""Re-derive grade + points for projects where the AI returned junk shape.

Symptom in prod: model returns `{"grade": "8", "points": 8}` for a positive
review on an Easy lesson — student gets gated at 90/100 despite a passing
verdict. Until the in-line normalizer (grok_service._normalize_grading_result)
shipped, those rows stayed stuck.

This script applies the same normalizer to existing rows WITHOUT re-calling
the AI. It uses the stored `points_earned` + `instructor_feedback` to fix
the obvious scale slip and derive the letter grade.

A project is a candidate when EITHER:
  - `grade` is not in {A, B, C, D, F} (e.g. literal "8", "8/10", numeric)
  - `grade` and `points_earned` disagree by more than one band
  - `points_earned` <= 10 and the feedback is strongly positive (scale slip)

Use --student-id N to scope to one student. --project-id N for a single row.

Usage:
    python scripts/normalize_misgraded_projects.py                 # dry-run
    python scripts/normalize_misgraded_projects.py --apply
    python scripts/normalize_misgraded_projects.py --student-id 52 --apply
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.project import Project  # noqa: E402
from app.services.grok_service import (  # noqa: E402
    _normalize_grading_result,
    _VALID_GRADES,
)


# A project that earned <90 should still update its `status` to reflect the
# new score: if we lift points above the threshold, mark it Under Review at
# minimum so the lesson gate releases. Don't overwrite Approved/Rejected.
PASS_THRESHOLD = 90


async def main(*, apply: bool, project_id: int | None, student_id: int | None) -> None:
    label = "APPLY" if apply else "DRY-RUN"
    print(f"=== Normalize misgraded projects ({label}) ===\n")

    async with AsyncSessionLocal() as db:
        stmt = select(Project)
        if project_id is not None:
            stmt = stmt.where(Project.id == project_id)
        elif student_id is not None:
            stmt = stmt.where(Project.student_id == student_id)
        rows = (await db.execute(stmt)).scalars().all()

        if not rows:
            print("No projects matched.")
            return

        touched = 0
        for p in rows:
            cur_grade = (p.grade or "").strip().upper()
            cur_points = int(p.points_earned or 0)

            # Skip rows that are obviously fine — letter grade in range AND
            # points consistent with that bucket — UNLESS the caller passed
            # --project-id, in which case force the row through.
            is_explicit = project_id is not None
            if not is_explicit and cur_grade in _VALID_GRADES:
                # Build a stub "result" and run the normalizer, see if it
                # actually changes anything.
                pass

            stub = {
                "grade": p.grade,
                "points": p.points_earned,
                "feedback": p.instructor_feedback or "",
                "summary": "",
            }
            fixed = _normalize_grading_result(stub, difficulty_level="Easy")
            new_grade = fixed["grade"]
            new_points = fixed["points"]

            changed = (new_grade != cur_grade) or (new_points != cur_points)
            if not changed:
                continue

            touched += 1
            print(f"  📝 project_id={p.id}  student_id={p.student_id}  "
                  f"title={(p.title or '')[:40]!r}")
            print(f"     grade : {cur_grade!r:6} → {new_grade!r}")
            print(f"     points: {cur_points:3} → {new_points:3}")

            if apply:
                p.grade = new_grade
                p.points_earned = new_points
                # Only nudge the status if (a) we're crossing the gate AND
                # (b) the status isn't a terminal teacher decision.
                if (new_points >= PASS_THRESHOLD
                        and p.status not in ("Approved", "Rejected")):
                    p.status = "Under Review"

        print(f"\nTouched {touched} project(s).")
        if apply:
            await db.commit()
            print("✓ COMMITTED.")
        else:
            await db.rollback()
            print("DRY-RUN: re-run with --apply to write.")

    await engine.dispose()


def cli() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="Write changes (default: dry-run).")
    parser.add_argument("--project-id", type=int, default=None,
                        help="Restrict to a single project id.")
    parser.add_argument("--student-id", type=int, default=None,
                        help="Restrict to all projects for one student id.")
    args = parser.parse_args()
    asyncio.run(main(
        apply=args.apply,
        project_id=args.project_id,
        student_id=args.student_id,
    ))


if __name__ == "__main__":
    cli()
