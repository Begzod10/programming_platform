"""Audit and repair the points invariant.

For each student, sum the source-of-truth rows and compare to
students.total_points. In `--apply` mode, corrects any drift by rewriting
students.total_points and mirroring to rankings.total_points inside a
single transaction, then re-ranks.

Identity:
    total_points ==
        SUM(exercise.points  where submission scored)
      + SUM(project.points_earned where Approved)
      + SUM(lesson.points_reward where completed)
      + SUM(achievement.points_reward where earned)
      + SUM(point_adjustments.delta)

The manual term is only reconstructable for adjustments made after the
audit ledger shipped. Older manual mutations will surface as drift here —
that's the correct answer; a human decides whether to insert a
compensating PointAdjustment row.

Usage:
    python scripts/recalc_points.py                    # report all
    python scripts/recalc_points.py --student-id 42    # report one
    python scripts/recalc_points.py --apply            # write corrections
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func, select  # noqa: E402

from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.achievement import Achievement  # noqa: E402
from app.models.exercise import Exercise, ExerciseSubmission  # noqa: E402
from app.models.lesson import Lesson, LessonCompletion  # noqa: E402
from app.models.point_adjustment import PointAdjustment  # noqa: E402
from app.models.project import Project  # noqa: E402
from app.models.ranking import Ranking  # noqa: E402
from app.models.student_achievement import StudentAchievement  # noqa: E402
from app.models.user import Student, UserRole  # noqa: E402


async def _sum_exercise_points(db, student_id: int) -> int:
    """SUM(exercise.points) over first-time scoring submissions."""
    scoring_subq = (
        select(ExerciseSubmission.exercise_id)
        .where(
            ExerciseSubmission.student_id == student_id,
            ExerciseSubmission.score > 0,
        )
        .distinct()
        .subquery()
    )
    stmt = select(func.coalesce(func.sum(Exercise.points), 0)).where(
        Exercise.id.in_(select(scoring_subq.c.exercise_id))
    )
    return int((await db.execute(stmt)).scalar() or 0)


async def _sum_project_points(db, student_id: int) -> int:
    stmt = select(func.coalesce(func.sum(Project.points_earned), 0)).where(
        Project.student_id == student_id,
        Project.status == "Approved",
    )
    return int((await db.execute(stmt)).scalar() or 0)


async def _sum_lesson_points(db, student_id: int) -> int:
    stmt = (
        select(func.coalesce(func.sum(Lesson.points_reward), 0))
        .select_from(LessonCompletion)
        .join(Lesson, Lesson.id == LessonCompletion.lesson_id)
        .where(LessonCompletion.student_id == student_id)
    )
    return int((await db.execute(stmt)).scalar() or 0)


async def _sum_achievement_points(db, student_id: int) -> int:
    stmt = (
        select(func.coalesce(func.sum(Achievement.points_reward), 0))
        .select_from(StudentAchievement)
        .join(Achievement, Achievement.id == StudentAchievement.achievement_id)
        .where(StudentAchievement.student_id == student_id)
    )
    return int((await db.execute(stmt)).scalar() or 0)


async def _sum_manual_adjustments(db, student_id: int) -> int:
    stmt = select(func.coalesce(func.sum(PointAdjustment.delta), 0)).where(
        PointAdjustment.student_id == student_id,
    )
    return int((await db.execute(stmt)).scalar() or 0)


async def _compute_for_student(db, student: Student) -> dict:
    ex_pts = await _sum_exercise_points(db, student.id)
    proj_pts = await _sum_project_points(db, student.id)
    lesson_pts = await _sum_lesson_points(db, student.id)
    ach_pts = await _sum_achievement_points(db, student.id)
    manual_pts = await _sum_manual_adjustments(db, student.id)
    expected = ex_pts + proj_pts + lesson_pts + ach_pts + manual_pts
    return {
        "student_id": student.id,
        "name": student.full_name or student.username,
        "current": int(student.total_points or 0),
        "expected": expected,
        "delta": expected - int(student.total_points or 0),
        "ex_pts": ex_pts,
        "proj_pts": proj_pts,
        "lesson_pts": lesson_pts,
        "ach_pts": ach_pts,
        "manual_pts": manual_pts,
    }


async def _apply_correction(db, student_id: int, expected: int) -> None:
    """Rewrite students.total_points and mirror to rankings.total_points.

    We do NOT route through RankingService.add_points_to_student here — the
    goal is to overwrite total_points to `expected`, not to bump it by a
    delta (which would trigger daily_points growth). We call
    calculate_and_update_rankings at the end to fix rank ordering.
    """
    st_res = await db.execute(select(Student).where(Student.id == student_id))
    student = st_res.scalar_one()
    student.total_points = expected

    rk_res = await db.execute(select(Ranking).where(Ranking.student_id == student_id))
    ranking = rk_res.scalar_one_or_none()
    if ranking is not None:
        ranking.total_points = expected


async def main(*, apply: bool, student_id: Optional[int]) -> None:
    label = "APPLY" if apply else "REPORT"
    print(f"=== Points recalc ({label}) ===\n")

    async with AsyncSessionLocal() as db:
        stmt = select(Student).where(Student.role == UserRole.student)
        if student_id is not None:
            stmt = stmt.where(Student.id == student_id)
        stmt = stmt.order_by(Student.id.asc())
        students = (await db.execute(stmt)).scalars().all()

        if not students:
            print("No students matched.")
            await engine.dispose()
            return

        header = (
            f"{'sid':>5}  {'name':<25}  "
            f"{'cur':>6} {'exp':>6} {'Δ':>5}  "
            f"{'ex':>5} {'proj':>5} {'les':>5} {'ach':>5} {'man':>5}"
        )
        print(header)
        print("-" * len(header))

        drifted = 0
        drift_total = 0
        for st in students:
            row = await _compute_for_student(db, st)
            if row["delta"] != 0:
                drifted += 1
                drift_total += abs(row["delta"])
            name = row["name"][:25]
            print(
                f"{row['student_id']:>5}  {name:<25}  "
                f"{row['current']:>6} {row['expected']:>6} {row['delta']:>5}  "
                f"{row['ex_pts']:>5} {row['proj_pts']:>5} "
                f"{row['lesson_pts']:>5} {row['ach_pts']:>5} {row['manual_pts']:>5}"
            )

            if apply and row["delta"] != 0:
                await _apply_correction(db, st.id, row["expected"])

        print()
        print(f"Checked {len(students)} students; drift on {drifted} "
              f"(sum |Δ| = {drift_total}).")

        if apply:
            # Recompute ranks after rewriting totals so global_rank stays in sync.
            from app.services.ranking_service import RankingService
            await RankingService(db).calculate_and_update_rankings()
            await db.commit()
            print("✓ COMMITTED. Ranks re-derived.")
        else:
            print("REPORT MODE: re-run with --apply to write corrections.")

    await engine.dispose()


def cli() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true",
        help="Write corrections (default: report only).",
    )
    parser.add_argument(
        "--student-id", type=int, default=None,
        help="Restrict to a single student id.",
    )
    args = parser.parse_args()
    asyncio.run(main(apply=args.apply, student_id=args.student_id))


if __name__ == "__main__":
    cli()
