from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload
from app.models.ranking import Ranking
from app.models.user import Student
from app.models.project import Project
from datetime import datetime, timedelta
from typing import List, Optional


async def calculate_and_update_rankings(db: AsyncSession):
    """Barcha studentlar uchun rankingni qayta hisoblaydi"""

    # Barcha studentlarni total_points bo'yicha tartiblash
    result = await db.execute(
        select(Student)
        .where(Student.is_active == True)
        .order_by(Student.total_points.desc())
    )
    students = result.scalars().all()

    for global_rank, student in enumerate(students, start=1):
        # Ranking mavjudmi tekshirish
        ranking_result = await db.execute(
            select(Ranking).where(Ranking.student_id == student.id)
        )
        ranking = ranking_result.scalar_one_or_none()

        # Tugallangan proyektlar soni
        projects_result = await db.execute(
            select(func.count(Project.id)).where(
                Project.student_id == student.id,
                Project.status == "Approved"
            )
        )
        projects_completed = projects_result.scalar() or 0

        # O'rtacha baho hisoblash
        avg_result = await db.execute(
            select(func.avg(Project.points_earned)).where(
                Project.student_id == student.id,
                Project.status == "Approved"
            )
        )
        average_grade = float(avg_result.scalar() or 0)

        # Level rank hisoblash
        level_result = await db.execute(
            select(Student)
            .where(
                Student.current_level == student.current_level,
                Student.is_active == True
            )
            .order_by(Student.total_points.desc())
        )
        level_students = level_result.scalars().all()
        level_rank = next(
            (i + 1 for i, s in enumerate(level_students) if s.id == student.id), 1
        )

        if ranking:
            ranking.total_points = student.total_points
            ranking.global_rank = global_rank
            ranking.level_rank = level_rank
            ranking.projects_completed = projects_completed
            ranking.average_grade = average_grade
            ranking.last_calculated_at = datetime.utcnow()
        else:
            new_ranking = Ranking(
                student_id=student.id,
                total_points=student.total_points,
                global_rank=global_rank,
                level_rank=level_rank,
                projects_completed=projects_completed,
                average_grade=average_grade,
                weekly_points=0,
                monthly_points=0,
                last_calculated_at=datetime.utcnow(),
            )
            db.add(new_ranking)

        # Student global_rank ni yangilash
        student.global_rank = global_rank

    await db.commit()


async def get_global_leaderboard(db: AsyncSession, limit: int = 10, offset: int = 0):
    """Global leaderboard"""
    result = await db.execute(
        select(Ranking)
        .join(Student, Ranking.student_id == Student.id)
        .where(Student.is_active == True)
        .order_by(Ranking.global_rank)
        .limit(limit)
        .offset(offset)
        .options(selectinload(Ranking.student))
    )
    return result.scalars().all()


async def get_level_leaderboard(db: AsyncSession, level: str, limit: int = 10):
    """Level bo'yicha leaderboard"""
    result = await db.execute(
        select(Ranking)
        .join(Student, Ranking.student_id == Student.id)
        .where(Student.current_level == level, Student.is_active == True)
        .order_by(Ranking.level_rank)
        .limit(limit)
        .options(selectinload(Ranking.student))
    )
    return result.scalars().all()


async def get_my_ranking(db: AsyncSession, student_id: int) -> Optional[Ranking]:
    """Studentning o'z rankingini olish"""
    result = await db.execute(
        select(Ranking)
        .where(Ranking.student_id == student_id)
        .options(selectinload(Ranking.student))
    )
    return result.scalar_one_or_none()


async def get_weekly_leaderboard(db: AsyncSession, limit: int = 10):
    """Haftalik leaderboard"""
    result = await db.execute(
        select(Ranking)
        .join(Student, Ranking.student_id == Student.id)
        .where(Student.is_active == True)
        .order_by(Ranking.weekly_points.desc())
        .limit(limit)
        .options(selectinload(Ranking.student))
    )
    return result.scalars().all()


async def get_monthly_leaderboard(db: AsyncSession, limit: int = 10):
    """Oylik leaderboard"""
    result = await db.execute(
        select(Ranking)
        .join(Student, Ranking.student_id == Student.id)
        .where(Student.is_active == True)
        .order_by(Ranking.monthly_points.desc())
        .limit(limit)
        .options(selectinload(Ranking.student))
    )
    return result.scalars().all()


async def add_points_to_student(db: AsyncSession, student_id: int, points: int):
    """Studentga point qo'shish va rankingni yangilash"""
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        return None

    student.total_points += points

    # Weekly va monthly points yangilash
    ranking_result = await db.execute(
        select(Ranking).where(Ranking.student_id == student_id)
    )
    ranking = ranking_result.scalar_one_or_none()
    if ranking:
        ranking.weekly_points += points
        ranking.monthly_points += points

    await db.commit()
    await calculate_and_update_rankings(db)
    return student


async def delete_ranking(db: AsyncSession, ranking_id: int) -> bool:
    """Rankingni o'chirish"""
    result = await db.execute(select(Ranking).where(Ranking.id == ranking_id))
    ranking = result.scalar_one_or_none()
    if not ranking:
        return False
    await db.delete(ranking)
    await db.commit()
    return True


async def create_ranking(db: AsyncSession, student_id: int) -> Optional[Ranking]:
    """Ranking yaratish"""
    existing = await db.execute(select(Ranking).where(Ranking.student_id == student_id))
    if existing.scalar_one_or_none():
        return None
    new_ranking = Ranking(
        student_id=student_id,
        total_points=0,
        global_rank=0,
        level_rank=0,
        projects_completed=0,
        average_grade=0.0,
        weekly_points=0,
        monthly_points=0,
    )
    db.add(new_ranking)
    await db.commit()
    await db.refresh(new_ranking)
    return new_ranking


async def update_ranking(db: AsyncSession, ranking_id: int, **kwargs) -> Optional[Ranking]:
    """Rankingni yangilash"""
    result = await db.execute(select(Ranking).where(Ranking.id == ranking_id))
    ranking = result.scalar_one_or_none()
    if not ranking:
        return None
    for key, value in kwargs.items():
        if value is not None:
            setattr(ranking, key, value)
    await db.commit()
    await db.refresh(ranking)
    return ranking
