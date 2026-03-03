import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.degree import Degree
from app.models.student_degree import StudentDegree
from app.models.user import Student
from app.models.project import Project
from typing import Optional, List
from datetime import datetime


async def get_all_degrees(db: AsyncSession) -> List[Degree]:
    """Barcha darajalarni olish"""
    result = await db.execute(select(Degree).order_by(Degree.required_points))
    return result.scalars().all()


async def get_degree_by_id(db: AsyncSession, degree_id: int) -> Optional[Degree]:
    """ID bo'yicha darajani olish"""
    result = await db.execute(select(Degree).where(Degree.id == degree_id))
    return result.scalar_one_or_none()


async def get_my_degrees(db: AsyncSession, student_id: int) -> List[StudentDegree]:
    """Studentning barcha darajalarini olish"""
    result = await db.execute(
        select(StudentDegree)
        .where(StudentDegree.student_id == student_id)
        .options(selectinload(StudentDegree.degree))
    )
    return result.scalars().all()


async def get_degree_progress(db: AsyncSession, student_id: int) -> List[dict]:
    """Studentning har bir daraja bo'yicha progressini hisoblash"""
    # Studentni olish
    student_result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        return []

    # Tugallangan proyektlar soni
    projects_result = await db.execute(
        select(Project)
        .where(Project.student_id == student_id, Project.status == "Approved")
    )
    completed_projects = len(projects_result.scalars().all())

    # Barcha darajalar
    degrees_result = await db.execute(select(Degree).order_by(Degree.required_points))
    degrees = degrees_result.scalars().all()

    # Studentning mavjud darajalari
    my_degrees_result = await db.execute(
        select(StudentDegree.degree_id).where(StudentDegree.student_id == student_id)
    )
    earned_degree_ids = set(my_degrees_result.scalars().all())

    progress_list = []
    for degree in degrees:
        points_progress = min(100, int((student.total_points / max(degree.required_points, 1)) * 100))
        projects_progress = min(100, int((completed_projects / max(degree.required_projects, 1)) * 100))
        overall_progress = (points_progress + projects_progress) // 2

        progress_list.append({
            "degree_id": degree.id,
            "degree_name": degree.name,
            "level": degree.level,
            "required_points": degree.required_points,
            "current_points": student.total_points,
            "points_progress": points_progress,
            "required_projects": degree.required_projects,
            "completed_projects": completed_projects,
            "projects_progress": projects_progress,
            "overall_progress": overall_progress,
            "is_earned": degree.id in earned_degree_ids,
        })

    return progress_list


async def award_degree(db: AsyncSession, student_id: int, degree_id: int) -> Optional[StudentDegree]:
    """Studentga daraja berish"""
    # Allaqachon bor-yo'qligini tekshirish
    existing = await db.execute(
        select(StudentDegree).where(
            StudentDegree.student_id == student_id,
            StudentDegree.degree_id == degree_id
        )
    )
    if existing.scalar_one_or_none():
        return None

    # Studentni tekshirish
    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalar_one_or_none()
    if not student:
        return None

    # Darajani tekshirish
    degree_result = await db.execute(select(Degree).where(Degree.id == degree_id))
    degree = degree_result.scalar_one_or_none()
    if not degree:
        return None

    # Talablarni tekshirish
    projects_result = await db.execute(
        select(Project).where(Project.student_id == student_id, Project.status == "Approved")
    )
    completed_projects = len(projects_result.scalars().all())

    if student.total_points < degree.required_points:
        return None
    if completed_projects < degree.required_projects:
        return None

    # Daraja berish
    verification_code = str(uuid.uuid4()).replace("-", "").upper()[:16]
    new_student_degree = StudentDegree(
        student_id=student_id,
        degree_id=degree_id,
        verification_code=verification_code,
        earned_at=datetime.utcnow(),
    )
    db.add(new_student_degree)
    await db.commit()
    await db.refresh(new_student_degree)
    return new_student_degree


async def verify_certificate(db: AsyncSession, verification_code: str) -> Optional[StudentDegree]:
    """Sertifikatni tekshirish"""
    result = await db.execute(
        select(StudentDegree)
        .where(StudentDegree.verification_code == verification_code)
        .options(selectinload(StudentDegree.student), selectinload(StudentDegree.degree))
    )
    return result.scalar_one_or_none()


async def check_and_award_degrees(db: AsyncSession, student_id: int) -> List[StudentDegree]:
    """Studentga avtomatik daraja berish tekshiruvi"""
    degrees_result = await db.execute(select(Degree).order_by(Degree.required_points))
    degrees = degrees_result.scalars().all()

    awarded = []
    for degree in degrees:
        result = await award_degree(db, student_id, degree.id)
        if result:
            awarded.append(result)

    return awarded


async def create_degree(db: AsyncSession, name: str, description: str, level: str, required_points: int,
                        required_projects: int, certificate_template: str, badge_image_url: str) -> Degree:
    """Yangi daraja yaratish"""
    new_degree = Degree(
        name=name,
        description=description,
        level=level,
        required_points=required_points,
        required_projects=required_projects,
        certificate_template=certificate_template,
        badge_image_url=badge_image_url,
    )
    db.add(new_degree)
    await db.commit()
    await db.refresh(new_degree)
    return new_degree


async def update_degree(db: AsyncSession, degree_id: int, **kwargs) -> Optional[Degree]:
    """Darajani yangilash"""
    degree = await get_degree_by_id(db, degree_id)
    if not degree:
        return None
    for key, value in kwargs.items():
        if value is not None:
            setattr(degree, key, value)
    await db.commit()
    await db.refresh(degree)
    return degree


async def delete_degree(db: AsyncSession, degree_id: int) -> bool:
    """Darajani o'chirish"""
    degree = await get_degree_by_id(db, degree_id)
    if not degree:
        return False
    await db.delete(degree)
    await db.commit()
    return True
