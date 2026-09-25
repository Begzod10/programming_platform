"""Category-level completion certificates — awarded once a student has
actually finished every course in a category (split into its own module
for the same "keep each service file under 800 lines" reason as
achievement_monitoring_service.py). Re-exported from achievement_service so
existing ``achievement_service.func_name`` call sites keep working.
"""
from typing import List, Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import Course
from app.models.lesson import Lesson
from app.models.student_achievement import CourseCertificate, CategoryCertificate


async def _required_course_ids(db: AsyncSession, category_id: int) -> List[int]:
    """Published+active courses in this category that have at least one
    active lesson (a course with none can't be completed, so it's skipped
    the same way _all_published_courses_complete skips one)."""
    result = await db.execute(
        select(Course.id).where(
            Course.category_id == category_id,
            Course.is_active == True,
            Course.is_published == True,
            select(func.count(Lesson.id))
                .where(Lesson.course_id == Course.id, Lesson.is_active == True)
                .scalar_subquery() > 0,
        )
    )
    return [r[0] for r in result.all()]


async def check_category_completion(db: AsyncSession, student_id: int, category_id: int) -> bool:
    """True iff the student has actually finished (100% of active lessons)
    every published+active course in this category. A category with no
    qualifying courses is never "complete".

    Checks real lesson completion (achievement_service.check_course_
    completion) rather than CourseCertificate existence — a student can
    finish every lesson in a course without a CourseCertificate row ever
    being minted for it: that row is a lazy side effect of the
    achievement-check flow (or an explicit course-certificate download),
    not something that fires deterministically the instant the last
    lesson is done. Keying off the certificate table under-reports
    completion — caught live in production: a student who'd 100%'d every
    course in a category still got "siz hali ... tugatmagansiz" because
    one course's CourseCertificate had simply never been minted.
    """
    from app.services.achievement_service import check_course_completion

    required_ids = await _required_course_ids(db, category_id)
    if not required_ids:
        return False

    for course_id in required_ids:
        if not await check_course_completion(db, student_id, course_id):
            return False
    return True


async def award_category_certificate(
    db: AsyncSession, student_id: int, category_id: int
) -> Optional[CategoryCertificate]:
    """Idempotent: mints a CategoryCertificate if the category is complete
    and the student doesn't already have one. Returns None otherwise."""
    existing_res = await db.execute(
        select(CategoryCertificate).where(
            and_(
                CategoryCertificate.student_id == student_id,
                CategoryCertificate.category_id == category_id,
            )
        )
    )
    if existing_res.scalar_one_or_none():
        return None

    if not await check_category_completion(db, student_id, category_id):
        return None

    # Backfill any CourseCertificate rows missing despite genuine
    # completion, so each individual course's certificate also becomes
    # downloadable right away (not just the category one) — same gap
    # check_category_completion's docstring explains. A direct insert,
    # not achievement_service.award_certificate(): that function's own
    # last step calls award_category_certificate() (the auto-award hook),
    # which would recurse straight back into this same function.
    required_ids = await _required_course_ids(db, category_id)
    held_res = await db.execute(
        select(CourseCertificate.course_id).where(
            CourseCertificate.student_id == student_id,
            CourseCertificate.course_id.in_(required_ids),
        )
    )
    held = {r[0] for r in held_res.all()}
    for course_id in required_ids:
        if course_id not in held:
            db.add(CourseCertificate(student_id=student_id, course_id=course_id))
    if len(held) < len(required_ids):
        await db.flush()

    cert = CategoryCertificate(student_id=student_id, category_id=category_id)
    db.add(cert)
    await db.commit()
    await db.refresh(cert)
    print(f"🎓 Yo'nalish sertifikati berildi: student={student_id}, category={category_id}, cert_id={cert.id}")
    return cert


async def get_category_certificate(
    db: AsyncSession, student_id: int, category_id: int
) -> Optional[CategoryCertificate]:
    result = await db.execute(
        select(CategoryCertificate)
        .options(selectinload(CategoryCertificate.category))
        .where(
            and_(
                CategoryCertificate.student_id == student_id,
                CategoryCertificate.category_id == category_id,
            )
        )
    )
    return result.scalar_one_or_none()
