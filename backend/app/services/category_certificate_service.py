"""Category-level completion certificates — awarded once a student holds a
CourseCertificate for every course in a category (mirrors the per-course
certificate logic in achievement_service.py; split into its own module for
the same "keep each service file under 800 lines" reason as
achievement_monitoring_service.py). Re-exported from achievement_service so
existing ``achievement_service.func_name`` call sites keep working.
"""
from typing import Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import Course
from app.models.lesson import Lesson
from app.models.student_achievement import CourseCertificate, CategoryCertificate


async def check_category_completion(db: AsyncSession, student_id: int, category_id: int) -> bool:
    """True iff the student holds a CourseCertificate for every published
    + active course in this category that has at least one active lesson —
    the same predicate _all_published_courses_complete uses, scoped to one
    category. A category with no qualifying courses is never "complete"."""
    course_res = await db.execute(
        select(Course.id).where(
            Course.category_id == category_id,
            Course.is_active == True,
            Course.is_published == True,
            select(func.count(Lesson.id))
                .where(Lesson.course_id == Course.id, Lesson.is_active == True)
                .scalar_subquery() > 0,
        )
    )
    required_ids = {r[0] for r in course_res.all()}
    if not required_ids:
        return False

    cert_res = await db.execute(
        select(CourseCertificate.course_id).where(
            CourseCertificate.student_id == student_id,
            CourseCertificate.course_id.in_(required_ids),
        )
    )
    held = {r[0] for r in cert_res.all()}
    return required_ids.issubset(held)


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
