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
