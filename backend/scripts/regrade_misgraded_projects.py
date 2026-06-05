"""Regrade student projects that were marked down by the old hardcoded
"Python/Flask" AI persona.

Background
----------
`app/services/grok_service.py:_build_review_prompt` previously opened with
"Sen tajribali Python/Flask o'qituvchisisiz". When students submitted
HTML/CSS or JavaScript projects, the AI penalized them for not using
Python/Flask. The prompt now takes lesson/course context and the persona
adapts — but historical submissions are still stuck on the old grade.

This script finds those historical miscored submissions and re-runs
grading with the new context-aware prompt against the same saved ZIP.

Match heuristic (kept conservative — we only touch obvious miscores)
-------------------------------------------------------------------
A submission is regraded when ALL hold:
  - `grade` is 'F' or 'D' (low grade where the rubric mismatch would
    plausibly have hurt)
  - `instructor_feedback` mentions "Python" or "Flask"
  - The parent lesson/course is NOT a Python course (course title
    doesn't contain "Python" or "Flask", case-insensitive)
  - A ZIP file still exists on disk for the project

Use `--dry-run` (default) to preview, `--apply` to write.
Use `--project-id N` to regrade a single project regardless of heuristic.

Usage
-----
    cd backend
    source venv/bin/activate

    # Preview which projects would be regraded
    python scripts/regrade_misgraded_projects.py

    # Actually run the AI and update grades
    python scripts/regrade_misgraded_projects.py --apply

    # Force-regrade one specific project (e.g. project 43)
    python scripts/regrade_misgraded_projects.py --project-id 43 --apply
"""
from __future__ import annotations

import argparse
import asyncio
import io
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.config import settings  # noqa: E402
from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.db import base as _base  # noqa: E402,F401
from app.models.course import Course  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.project import Project  # noqa: E402
from app.models.submission import Submission  # noqa: E402
from app.services.grok_service import analyze_project_with_grok  # noqa: E402


PROJECTS_UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "projects"

CODE_EXTS = (
    ".html", ".css", ".js", ".py",
    ".ts", ".jsx", ".tsx", ".vue",
    ".java", ".php", ".cpp", ".c",
)

PYTHON_COURSE_HINTS = ("python", "flask", "django", "fastapi")

FEEDBACK_TRIGGER_WORDS = ("python", "flask")
LOW_GRADES = {"F", "D"}


@dataclass
class Candidate:
    project_id: int
    student_id: int
    lesson_id: Optional[int]
    course_id: Optional[int]
    course_title: Optional[str]
    lesson_title: Optional[str]
    old_grade: Optional[str]
    old_points: int
    zip_path: Path
    project_title: str


def _read_zip_code(zip_path: Path) -> str:
    """Re-read the same ZIP the AI saw the first time. Capped at 10 files /
    2k chars per file to match the original upload endpoint exactly."""
    if not zip_path.exists():
        return ""
    try:
        with zipfile.ZipFile(zip_path) as zf:
            real = [n for n in zf.namelist() if not n.endswith("/")]
            out = ""
            for name in real[:10]:
                if any(name.endswith(ext) for ext in CODE_EXTS):
                    try:
                        with zf.open(name) as f:
                            code = f.read().decode("utf-8", errors="ignore")
                            out += f"\n\n=== {name} ===\n{code[:2000]}"
                    except Exception:
                        pass
            return out
    except zipfile.BadZipFile:
        return ""


async def _build_lesson_context(db, project_id: int) -> Optional[dict]:
    """Same lookup as the endpoint helper, copied here so the script
    doesn't depend on importing the FastAPI module (avoids triggering
    full app startup)."""
    row = (await db.execute(
        select(Submission.lesson_id)
        .where(Submission.project_id == project_id)
        .where(Submission.lesson_id.is_not(None))
        .order_by(Submission.id.desc())
        .limit(1)
    )).first()
    if not row or row[0] is None:
        return None
    lesson_id = row[0]

    lesson = (await db.execute(
        select(Lesson).where(Lesson.id == lesson_id)
    )).scalar_one_or_none()
    if lesson is None:
        return None

    course = (await db.execute(
        select(Course).where(Course.id == lesson.course_id)
    )).scalar_one_or_none()

    return {
        "course_title": course.title if course else None,
        "course_difficulty": course.difficulty_level if course else None,
        "lesson_title": lesson.title,
        "lesson_order": lesson.order,
        "lesson_code_language": lesson.code_language,
        "task_title": lesson.task_title,
        "task_description": lesson.task_description,
        "task_requirements": lesson.task_requirements,
        "task_technologies": lesson.task_technologies,
    }


def _is_python_course(course_title: Optional[str]) -> bool:
    if not course_title:
        return False
    low = course_title.lower()
    return any(hint in low for hint in PYTHON_COURSE_HINTS)


def _feedback_mentions_python(feedback: Optional[str]) -> bool:
    if not feedback:
        return False
    low = feedback.lower()
    return any(word in low for word in FEEDBACK_TRIGGER_WORDS)


async def _find_candidates(db, *, force_project_id: Optional[int]) -> list[Candidate]:
    """If `force_project_id` is set, returns that single project
    unconditionally. Otherwise filters by the miscore heuristic."""
    query = (
        select(
            Project.id, Project.student_id, Project.title,
            Project.grade, Project.points_earned, Project.project_files,
            Project.instructor_feedback,
            Submission.lesson_id, Lesson.course_id, Lesson.title,
            Course.title,
        )
        .select_from(Project)
        .outerjoin(Submission, Submission.project_id == Project.id)
        .outerjoin(Lesson, Lesson.id == Submission.lesson_id)
        .outerjoin(Course, Course.id == Lesson.course_id)
    )
    if force_project_id is not None:
        query = query.where(Project.id == force_project_id)

    rows = (await db.execute(query)).all()

    candidates: list[Candidate] = []
    missing_zip: list[tuple[int, Path]] = []
    for r in rows:
        (pid, sid, ptitle, grade, points, files, feedback,
         lesson_id, course_id, lesson_title, course_title) = r

        if not files:
            continue
        zip_path = PROJECTS_UPLOAD_DIR / Path(files).name

        if force_project_id is None:
            if grade not in LOW_GRADES:
                continue
            if not _feedback_mentions_python(feedback):
                continue
            if _is_python_course(course_title):
                # Real Python project that just failed legitimately —
                # don't second-guess.
                continue

        if not zip_path.exists():
            missing_zip.append((pid, zip_path))
            # Still surface it as a candidate for dry-run visibility,
            # but flag the zip_path so apply-mode will skip it cleanly.
            candidates.append(Candidate(
                project_id=pid,
                student_id=sid,
                lesson_id=lesson_id,
                course_id=course_id,
                course_title=course_title,
                lesson_title=lesson_title,
                old_grade=grade,
                old_points=points or 0,
                zip_path=zip_path,
                project_title=ptitle or "",
            ))
            continue

        candidates.append(Candidate(
            project_id=pid,
            student_id=sid,
            lesson_id=lesson_id,
            course_id=course_id,
            course_title=course_title,
            lesson_title=lesson_title,
            old_grade=grade,
            old_points=points or 0,
            zip_path=zip_path,
            project_title=ptitle or "",
        ))

    if missing_zip:
        print(
            f"⚠️  {len(missing_zip)} candidate ZIP(s) missing on this host "
            f"(run on the server with the uploads dir):"
        )
        for pid, p in missing_zip[:10]:
            print(f"     project {pid}: {p}")
        if len(missing_zip) > 10:
            print(f"     … and {len(missing_zip) - 10} more")
        print()

    return candidates


async def _regrade_one(db, cand: Candidate, *, apply: bool) -> dict:
    code = _read_zip_code(cand.zip_path)
    ctx = await _build_lesson_context(db, cand.project_id)

    project = (await db.execute(
        select(Project).where(Project.id == cand.project_id)
    )).scalar_one_or_none()
    if project is None:
        return {"error": "project_vanished"}

    technologies: list[str] = []
    if project.technologies_used:
        if isinstance(project.technologies_used, list):
            technologies = project.technologies_used
        else:
            technologies = [project.technologies_used]

    ai_result = await analyze_project_with_grok(
        title=project.title,
        description=(project.description or "") + (
            f"\n\nKod fayllari:\n{code}" if code else ""
        ),
        github_url=project.github_url or "ZIP fayl orqali yuklandi",
        technologies=technologies,
        difficulty_level=project.difficulty_level,
        previous_points=project.points_earned or 0,
        lesson_context=ctx,
    )

    if ai_result.get("error"):
        return {"error": ai_result["error"], "ai_message": ai_result.get("feedback")}

    new_grade = ai_result.get("grade")
    new_points = ai_result.get("points", 0)

    if apply:
        project.grade = new_grade
        project.points_earned = new_points
        project.instructor_feedback = ai_result.get("feedback", "")
        project.status = "Under Review"
        await db.commit()

    return {
        "old_grade": cand.old_grade,
        "old_points": cand.old_points,
        "new_grade": new_grade,
        "new_points": new_points,
        "provider": ai_result.get("provider"),
        "lesson_context_used": ctx is not None,
    }


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Regrade projects miscored by the old Python/Flask AI persona",
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Actually update DB. Default is dry-run (lists candidates only).",
    )
    parser.add_argument(
        "--project-id", type=int, default=None,
        help="Force-regrade a single project, skipping the miscore heuristic.",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Cap the number of regrades (useful for testing on prod).",
    )
    args = parser.parse_args()

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[{mode}] Regrade misgraded projects")
    print(f"  Uploads dir: {PROJECTS_UPLOAD_DIR}")
    print(f"  Forced project_id: {args.project_id}")
    print()

    async with AsyncSessionLocal() as db:
        candidates = await _find_candidates(db, force_project_id=args.project_id)

        if args.limit is not None:
            candidates = candidates[: args.limit]

        if not candidates:
            print("No candidates found.")
            await engine.dispose()
            return

        print(f"Found {len(candidates)} candidate(s):")
        for c in candidates:
            print(
                f"  - project {c.project_id} student {c.student_id} "
                f"grade={c.old_grade} points={c.old_points} "
                f"course={c.course_title!r} lesson={c.lesson_title!r}"
            )
        print()

        if not args.apply:
            print("Dry-run: pass --apply to actually regrade.")
            await engine.dispose()
            return

        # Apply phase. Sequential — we don't want to hammer the AI provider.
        ok = 0
        failed = 0
        for c in candidates:
            if not c.zip_path.exists():
                failed += 1
                print(f"   ⏭️  project {c.project_id} skipped (ZIP missing: {c.zip_path})")
                continue
            print(f"→ Regrading project {c.project_id} (course={c.course_title!r}) …")
            try:
                result = await _regrade_one(db, c, apply=True)
            except Exception as e:  # noqa: BLE001 — surface anything, keep going
                failed += 1
                print(f"   ❌ exception: {e!r}")
                continue

            if result.get("error"):
                failed += 1
                print(f"   ❌ AI error: {result['error']}")
            else:
                ok += 1
                print(
                    f"   ✅ {result['old_grade']}({result['old_points']}) → "
                    f"{result['new_grade']}({result['new_points']}) "
                    f"provider={result.get('provider')} "
                    f"ctx={result['lesson_context_used']}"
                )

        print()
        print(f"Done. Regraded {ok}, failed {failed}.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
