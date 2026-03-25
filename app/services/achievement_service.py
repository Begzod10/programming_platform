from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.achievement import Achievement
from app.models.student_achievement import StudentAchievement
from app.models.user import Student
from app.models.project import Project
from typing import Optional, List
from datetime import datetime


async def get_all_achievements(db: AsyncSession) -> List[Achievement]:
    """Barcha achievementlarni olish"""
    result = await db.execute(select(Achievement).order_by(Achievement.points_reward))
    return result.scalars().all()


async def get_achievement_by_id(db: AsyncSession, achievement_id: int) -> Optional[Achievement]:
    """ID bo'yicha achievement olish"""
    result = await db.execute(select(Achievement).where(Achievement.id == achievement_id))
    return result.scalar_one_or_none()


async def get_my_achievements(db: AsyncSession, student_id: int) -> List[StudentAchievement]:
    """Studentning barcha achievementlarini olish"""
    result = await db.execute(
        select(StudentAchievement)
        .where(StudentAchievement.student_id == student_id)
        .options(selectinload(StudentAchievement.achievement))
    )
    return result.scalars().all()


async def get_achievement_progress(db: AsyncSession, student_id: int) -> List[dict]:
    """Studentning achievement progressini hisoblash"""
    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalar_one_or_none()
    if not student:
        return []

    # Tugallangan proyektlar soni
    projects_result = await db.execute(
        select(func.count(Project.id)).where(
            Project.student_id == student_id,
            Project.status == "Approved"
        )
    )
    completed_projects = projects_result.scalar() or 0

    # Barcha achievementlar
    achievements_result = await db.execute(select(Achievement))
    achievements = achievements_result.scalars().all()

    # Studentning mavjud achievementlari
    my_achievements_result = await db.execute(
        select(StudentAchievement.achievement_id)
        .where(StudentAchievement.student_id == student_id)
    )
    earned_ids = set(my_achievements_result.scalars().all())

    progress_list = []
    for ach in achievements:
        if ach.criteria_type == "project_count":
            current = completed_projects
        elif ach.criteria_type == "points_threshold":
            current = student.total_points
        else:
            current = 0

        progress = min(100, int((current / max(ach.criteria_value, 1)) * 100))

        progress_list.append({
            "achievement_id": ach.id,
            "name": ach.name,
            "description": ach.description,
            "badge_image_url": ach.badge_image_url,
            "points_reward": ach.points_reward,
            "criteria_type": ach.criteria_type,
            "criteria_value": ach.criteria_value,
            "current_value": current,
            "progress": progress,
            "is_earned": ach.id in earned_ids,
        })

    return progress_list


async def award_achievement(db: AsyncSession, student_id: int, achievement_id: int) -> Optional[StudentAchievement]:
    """Studentga achievement berish"""
    existing = await db.execute(
        select(StudentAchievement).where(
            StudentAchievement.student_id == student_id,
            StudentAchievement.achievement_id == achievement_id
        )
    )
    if existing.scalar_one_or_none():
        return None

    achievement_result = await db.execute(select(Achievement).where(Achievement.id == achievement_id))
    achievement = achievement_result.scalar_one_or_none()
    if not achievement:
        return None

    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalar_one_or_none()
    if not student:
        return None

    # Point qo'shish
    student.total_points += achievement.points_reward

    new_achievement = StudentAchievement(
        student_id=student_id,
        achievement_id=achievement_id,
        earned_at=datetime.utcnow(),
    )
    db.add(new_achievement)
    await db.commit()
    await db.refresh(new_achievement)
    return new_achievement


async def check_and_award_achievements(db: AsyncSession, student_id: int) -> List[StudentAchievement]:
    """Avtomatik achievement tekshiruvi"""
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

    achievements_result = await db.execute(select(Achievement))
    achievements = achievements_result.scalars().all()

    awarded = []
    for ach in achievements:
        if ach.criteria_type == "project_count" and completed_projects >= ach.criteria_value:
            result = await award_achievement(db, student_id, ach.id)
            if result:
                awarded.append(result)
        elif ach.criteria_type == "points_threshold" and student.total_points >= ach.criteria_value:
            result = await award_achievement(db, student_id, ach.id)
            if result:
                awarded.append(result)

    return awarded


async def create_achievement(db: AsyncSession, name: str, description: str, badge_image_url: str, points_reward: int,
                             criteria_type: str, criteria_value: int) -> Achievement:
    """Yangi achievement yaratish"""
    new_achievement = Achievement(
        name=name,
        description=description,
        badge_image_url=badge_image_url,
        points_reward=points_reward,
        criteria_type=criteria_type,
        criteria_value=criteria_value,
    )
    db.add(new_achievement)
    await db.commit()
    await db.refresh(new_achievement)
    return new_achievement


async def update_achievement(db: AsyncSession, achievement_id: int, **kwargs) -> Optional[Achievement]:
    """Achievementni yangilash"""
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
    """Achievementni o'chirish"""
    achievement = await get_achievement_by_id(db, achievement_id)
    if not achievement:
        return False
    await db.delete(achievement)
    await db.commit()
    return True


# ✅ YANGI - Teacher uchun
async def get_students_with_achievement(db: AsyncSession, achievement_id: int) -> List[dict]:
    """Sertifikat olgan studentlar"""
    result = await db.execute(
        select(StudentAchievement)
        .options(selectinload(StudentAchievement.student))
        .where(StudentAchievement.achievement_id == achievement_id)
    )
    student_achievements = result.scalars().all()

    return [
        {
            "student_id": sa.student_id,
            "username": sa.student.username,
            "full_name": sa.student.full_name,
            "email": sa.student.email,
            "earned_at": sa.earned_at,
            "total_points": sa.student.total_points,
            "current_level": sa.student.current_level.value
        }
        for sa in student_achievements
    ]


async def get_students_without_achievement(db: AsyncSession, achievement_id: int) -> List[dict]:
    """Sertifikat olmagan studentlar"""
    # Achievement olgan studentlar ID'lari
    earned_result = await db.execute(
        select(StudentAchievement.student_id)
        .where(StudentAchievement.achievement_id == achievement_id)
    )
    earned_ids = set(earned_result.scalars().all())

    # Barcha studentlar
    all_students_result = await db.execute(select(Student))
    all_students = all_students_result.scalars().all()

    # Achievement olmagan studentlar
    students_without = [
        {
            "student_id": student.id,
            "username": student.username,
            "full_name": student.full_name,
            "email": student.email,
            "total_points": student.total_points,
            "current_level": student.current_level.value,
            "progress": await _calculate_student_progress(db, student.id, achievement_id)
        }
        for student in all_students
        if student.id not in earned_ids
    ]

    return students_without


async def _calculate_student_progress(db: AsyncSession, student_id: int, achievement_id: int) -> int:
    """Student progressini hisoblash (helper)"""
    achievement_result = await db.execute(
        select(Achievement).where(Achievement.id == achievement_id)
    )
    achievement = achievement_result.scalar_one_or_none()
    if not achievement:
        return 0

    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalar_one_or_none()
    if not student:
        return 0

    if achievement.criteria_type == "project_count":
        projects_result = await db.execute(
            select(func.count(Project.id)).where(
                Project.student_id == student_id,
                Project.status == "Approved"
            )
        )
        current = projects_result.scalar() or 0
    elif achievement.criteria_type == "points_threshold":
        current = student.total_points
    else:
        current = 0

    return min(100, int((current / max(achievement.criteria_value, 1)) * 100))


async def get_achievement_statistics(db: AsyncSession, achievement_id: int) -> dict:
    """Achievement statistikasi"""
    achievement_result = await db.execute(
        select(Achievement).where(Achievement.id == achievement_id)
    )
    achievement = achievement_result.scalar_one_or_none()
    if not achievement:
        return {}

    # Olganlar soni
    earned_count_result = await db.execute(
        select(func.count(StudentAchievement.id))
        .where(StudentAchievement.achievement_id == achievement_id)
    )
    earned_count = earned_count_result.scalar() or 0

    # Jami studentlar
    total_students_result = await db.execute(select(func.count(Student.id)))
    total_students = total_students_result.scalar() or 0

    # Olmagan studentlar
    not_earned_count = total_students - earned_count

    # Foiz
    percentage = (earned_count / total_students * 100) if total_students > 0 else 0

    return {
        "achievement_id": achievement.id,
        "achievement_name": achievement.name,
        "total_students": total_students,
        "students_earned": earned_count,
        "students_not_earned": not_earned_count,
        "completion_percentage": round(percentage, 2)
    }
