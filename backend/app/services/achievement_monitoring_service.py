"""Monitoring, progress tracking, statistics, and CRUD for achievements.

Split from achievement_service.py to keep each module under 800 lines.
All public symbols here are re-exported from achievement_service for
backwards-compatible ``achievement_service.func_name`` call sites.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.achievement import Achievement
from app.models.student_achievement import StudentAchievement, CourseCertificate
from app.models.user import Student
from app.models.project import Project
from app.models.lesson import LessonCompletion
from app.models.dictionary import UserDictionary
from typing import Optional, List


# ========== MONITORING & PROGRESS ==========

async def get_achievement_progress(db: AsyncSession, student_id: int) -> List[dict]:
    """Studentning barcha achievementlar bo'yicha progressini hisoblash"""
    # Lazy import to avoid circular dependency with achievement_service
    from app.services.achievement_service import get_all_achievements

    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalar_one_or_none()
    if not student:
        return []

    projects_result = await db.execute(
        select(func.count(Project.id)).where(
            Project.student_id == student_id,
            Project.status == "Approved"
        )
    )
    completed_projects = projects_result.scalar() or 0

    achievements = await get_all_achievements(db)

    my_sa_result = await db.execute(
        select(StudentAchievement.achievement_id).where(StudentAchievement.student_id == student_id)
    )
    earned_ids = set(my_sa_result.scalars().all())

    progress_list = []
    for ach in achievements:
        current = 0
        target = ach.criteria_value or 1
        pct = 0

        if ach.criteria_type == "project_count":
            current = completed_projects
            pct = min(100, int((current / target) * 100))
        elif ach.criteria_type == "course_completion":
            if ach.course_id:
                # Kurs progressini foizda olamiz
                from app.services.course_service import CourseService
                pct = await CourseService.calc_progress(db, ach.course_id, student_id)
                current = 1 if pct >= 100 else 0
            else:
                # Agar course_id yo'q bo'lsa, progress 0 bo'lishi kerak
                current = 0
                pct = 0
        elif ach.criteria_type == "points_threshold":
            current = student.total_points
            pct = min(100, int((current / target) * 100))
        elif ach.criteria_type == "lesson_count":
            lc_res = await db.execute(
                select(func.count(LessonCompletion.id)).where(
                    LessonCompletion.student_id == student_id
                )
            )
            current = lc_res.scalar() or 0
            pct = min(100, int((current / target) * 100))
        elif ach.criteria_type == "word_count":
            wc_res = await db.execute(
                select(func.count(UserDictionary.id)).where(
                    UserDictionary.student_id == student_id
                )
            )
            current = wc_res.scalar() or 0
            pct = min(100, int((current / target) * 100))
        elif ach.criteria_type == "course_count":
            cc_res = await db.execute(
                select(func.count(CourseCertificate.id)).where(
                    CourseCertificate.student_id == student_id
                )
            )
            current = cc_res.scalar() or 0
            pct = min(100, int((current / target) * 100))
        else:
            # Boshqa turlar uchun progress hozircha 0
            current = 0
            pct = 0

        progress_list.append({
            "achievement_id": ach.id,
            "name": ach.name,
            "description": ach.description,
            "badge_image_url": ach.badge_image_url,
            "points_reward": ach.points_reward,
            "criteria_type": ach.criteria_type,
            "criteria_value": target,
            "current_value": current,
            "progress": pct,
            "is_earned": ach.id in earned_ids,
            "category": getattr(ach, "category", "general"),
            "icon": getattr(ach, "icon", "🏆"),
        })
    return progress_list


async def get_students_with_achievement(db: AsyncSession, achievement_id: int) -> List[dict]:
    """Sertifikat olgan studentlar ro'yxati"""
    result = await db.execute(
        select(StudentAchievement)
        .options(selectinload(StudentAchievement.student))
        .where(StudentAchievement.achievement_id == achievement_id)
    )
    return [
        {
            "student_id": sa.student_id,
            "username": sa.student.username,
            "full_name": sa.student.full_name or sa.student.username,
            "email": sa.student.email,
            "earned_at": sa.earned_at,
            "total_points": sa.student.total_points,
            "current_level": sa.student.current_level.value
        }
        for sa in result.scalars().all()
    ]


async def get_students_without_achievement(db: AsyncSession, achievement_id: int) -> List[dict]:
    """Sertifikat olmagan studentlar ro'yxati"""
    earned_result = await db.execute(
        select(StudentAchievement.student_id).where(StudentAchievement.achievement_id == achievement_id)
    )
    earned_ids = set(earned_result.scalars().all())

    all_students_result = await db.execute(select(Student))
    all_students = all_students_result.scalars().all()

    students_without = []
    for student in all_students:
        if student.id not in earned_ids:
            progress = await _calculate_student_progress(db, student.id, achievement_id)
            students_without.append({
                "student_id": student.id,
                "username": student.username,
                "full_name": student.full_name or student.username,
                "email": student.email,
                "total_points": student.total_points,
                "current_level": student.current_level.value,
                "progress": progress
            })
    return students_without


async def _calculate_student_progress(db: AsyncSession, student_id: int, achievement_id: int) -> int:
    # Lazy import to avoid circular dependency with achievement_service
    from app.services.achievement_service import get_achievement_by_id, check_course_completion

    ach = await get_achievement_by_id(db, achievement_id)
    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalar_one_or_none()

    if not ach or not student:
        return 0

    if ach.criteria_type == "project_count":
        res = await db.execute(
            select(func.count(Project.id)).where(
                Project.student_id == student_id,
                Project.status == "Approved"
            )
        )
        current = res.scalar() or 0
    elif ach.criteria_type == "course_completion" and ach.course_id:
        current = 1 if await check_course_completion(db, student_id, ach.course_id) else 0
    else:
        current = student.total_points

    return min(100, int((current / max(ach.criteria_value, 1)) * 100))


async def get_achievement_statistics(db: AsyncSession, achievement_id: int) -> dict:
    """Achievement bo'yicha umumiy statistika"""
    # Lazy import to avoid circular dependency with achievement_service
    from app.services.achievement_service import get_achievement_by_id

    ach = await get_achievement_by_id(db, achievement_id)
    if not ach:
        return {}

    earned_count_res = await db.execute(
        select(func.count(StudentAchievement.id)).where(StudentAchievement.achievement_id == achievement_id)
    )
    earned_count = earned_count_res.scalar() or 0

    total_students_res = await db.execute(select(func.count(Student.id)))
    total_students = total_students_res.scalar() or 0

    percentage = round((earned_count / total_students * 100), 2) if total_students > 0 else 0

    return {
        "achievement_id": ach.id,
        "achievement_name": ach.name,
        "total_students": total_students,
        "students_earned": earned_count,
        "students_not_earned": total_students - earned_count,
        "completion_percentage": percentage
    }


# ========== CRUD ==========

async def create_achievement(db: AsyncSession, **kwargs) -> Achievement:
    new_achievement = Achievement(**kwargs)
    db.add(new_achievement)
    await db.commit()
    await db.refresh(new_achievement)
    return new_achievement


async def update_achievement(db: AsyncSession, achievement_id: int, **kwargs) -> Optional[Achievement]:
    # Lazy import to avoid circular dependency with achievement_service
    from app.services.achievement_service import get_achievement_by_id

    achievement = await get_achievement_by_id(db, achievement_id)
    if not achievement:
        return None
    for key, value in kwargs.items():
        if value is not None:
            setattr(achievement, key, value)
    await db.commit()
    await db.refresh(achievement)
    return achievement


async def delete_achievement(db: AsyncSession, achievement_id: int) -> bool:
    # Lazy import to avoid circular dependency with achievement_service
    from app.services.achievement_service import get_achievement_by_id

    achievement = await get_achievement_by_id(db, achievement_id)
    if not achievement:
        return False
    await db.delete(achievement)
    await db.commit()
    return True


async def force_sync_all_levels(db: AsyncSession):
    result = await db.execute(select(Student))
    students = result.scalars().all()
    for student in students:
        student.total_points = student.total_points
    await db.commit()
    return {"status": "done"}
