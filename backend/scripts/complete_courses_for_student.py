"""Mark every active lesson of the given courses as completed for one student
(and enroll them in those courses). For test accounts — it fabricates
completions only: no points, no projects, no submissions.

    cd /home/student_platform/backend && source venv/bin/activate
    python scripts/complete_courses_for_student.py --student test_sherzd \
        --course "HTML CSS" --course "HTML/CSS Mini-Projects"

Course titles are matched exactly (case-insensitive). Re-running is safe.
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.db import base as _base  # noqa: F401
from app.db.database import AsyncSessionLocal
from app.models.course import Course, student_courses
from app.models.lesson import Lesson, LessonCompletion
from app.models.user import Student


async def main(username: str, titles: list) -> None:
    async with AsyncSessionLocal() as db:
        st = (await db.execute(select(Student).where(Student.username == username))).scalar_one_or_none()
        if st is None:
            sys.exit(f"student not found: {username}")
        print(f"student: {st.username} (id {st.id}, {st.full_name})")
        for title in titles:
            courses = (await db.execute(
                select(Course).where(func.lower(Course.title) == title.strip().lower())
            )).scalars().all()
            if not courses:
                print(f"  ! course not found: {title}")
                continue
            for c in courses:
                lessons = (await db.execute(
                    select(Lesson.id).where(Lesson.course_id == c.id, Lesson.is_active.is_(True))
                )).scalars().all()
                before = (await db.execute(
                    select(func.count(LessonCompletion.id)).where(
                        LessonCompletion.student_id == st.id, LessonCompletion.lesson_id.in_(lessons))
                )).scalar() or 0
                if lessons:
                    await db.execute(
                        pg_insert(LessonCompletion).values(
                            [{"student_id": st.id, "lesson_id": lid} for lid in lessons]
                        ).on_conflict_do_nothing(constraint="uq_student_lesson_completion")
                    )
                await db.execute(
                    pg_insert(student_courses).values(student_id=st.id, course_id=c.id).on_conflict_do_nothing()
                )
                print(f"  {c.title} (id {c.id}): {len(lessons)} lessons, {before} already done -> all done")
        await db.commit()
        print("COMMITTED.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--student", required=True)
    ap.add_argument("--course", action="append", required=True)
    a = ap.parse_args()
    asyncio.run(main(a.student, a.course))
