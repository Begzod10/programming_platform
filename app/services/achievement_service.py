from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.achievement import Achievement
from app.models.student_achievement import StudentAchievement
from app.models.user import Student
from app.models.project import Project
from typing import Optional, List
from datetime import datetime
from app.models.lesson import Lesson
from app.models.submission import Submission
from app.models.student_achievement import CourseCertificate
from sqlalchemy import and_

import os
import io
from app.utils.certificate import generate_certificate, generate_badge_certificate
from app.models.student_achievement import CourseCertificate, StudentAchievement
from app.models.achievement import Achievement
from app.models.user import Student
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import Optional, Union


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


# ========== CORE LOGIC (AWARD / REVOKE / CHECK) ==========

async def award_achievement(db: AsyncSession, student_id: int, achievement_id: int) -> Optional[StudentAchievement]:
    """Studentga achievement berish, ball qo'shish va darajani yangilash"""
    # 1. Allaqachon borligini tekshirish
    existing = await db.execute(
        select(StudentAchievement).where(
            StudentAchievement.student_id == student_id,
            StudentAchievement.achievement_id == achievement_id
        )
    )
    if existing.scalar_one_or_none():
        return None

    # 2. Achievement va Studentni yuklash
    achievement = await get_achievement_by_id(db, achievement_id)
    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalar_one_or_none()

    if not student or not achievement:
        return None

    # 3. Ballarni qo'shish va Darajani yangilash
    student.total_points += achievement.points_reward
    if hasattr(student, 'update_level_based_on_points'):
        student.update_level_based_on_points()

    # 4. Saqlash
    new_sa = StudentAchievement(
        student_id=student_id,
        achievement_id=achievement_id,
        earned_at=datetime.utcnow()
    )
    db.add(new_sa)
    await db.commit()
    await db.refresh(new_sa)
    return new_sa


async def revoke_achievement(db: AsyncSession, student_id: int, achievement_id: int) -> bool:
    """Studentdan achievementni qaytib olish, ballarni ayirish va darajani qayta hisoblash"""
    # 1. Bog'liqlikni qidirish
    result = await db.execute(
        select(StudentAchievement).where(
            StudentAchievement.student_id == student_id,
            StudentAchievement.achievement_id == achievement_id
        )
    )
    student_achievement = result.scalar_one_or_none()
    if not student_achievement:
        return False

    # 2. Achievement va Student ma'lumotlarini olish
    achievement = await get_achievement_by_id(db, achievement_id)
    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalar_one_or_none()

    # 3. Ballarni ayirish va darajani qayta hisoblash
    if student and achievement:
        student.total_points = max(0, student.total_points - achievement.points_reward)
        if hasattr(student, 'update_level_based_on_points'):
            student.update_level_based_on_points()

    # 4. O'chirish
    await db.delete(student_achievement)
    await db.commit()
    return True


async def check_and_award_achievements(db: AsyncSession, student_id: int) -> List[StudentAchievement]:
    """Avtomatik achievement tekshiruvi (kriteriyalar bo'yicha)"""
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

    # Barcha mavjud achievementlar
    achievements = await get_all_achievements(db)

    awarded = []
    for ach in achievements:
        should_award = False
        if ach.criteria_type == "project_count" and completed_projects >= ach.criteria_value:
            should_award = True
        elif ach.criteria_type == "points_threshold" and student.total_points >= ach.criteria_value:
            should_award = True

        if should_award:
            result = await award_achievement(db, student_id, ach.id)
            if result:
                awarded.append(result)
    return awarded


# ========== MONITORING & PROGRESS ==========

async def get_achievement_progress(db: AsyncSession, student_id: int) -> List[dict]:
    """Studentning barcha achievementlar bo'yicha progressini hisoblash"""
    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalar_one_or_none()
    if not student:
        return []

    # Proyektlar soni
    projects_result = await db.execute(
        select(func.count(Project.id)).where(
            Project.student_id == student_id,
            Project.status == "Approved"
        )
    )
    completed_projects = projects_result.scalar() or 0

    achievements = await get_all_achievements(db)

    # Studentning olingan yutuqlari ID'lari
    my_sa_result = await db.execute(
        select(StudentAchievement.achievement_id).where(StudentAchievement.student_id == student_id)
    )
    earned_ids = set(my_sa_result.scalars().all())

    progress_list = []
    for ach in achievements:
        current = completed_projects if ach.criteria_type == "project_count" else student.total_points
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
    """Sertifikat olmagan studentlar ro'yxati va ularning progressi"""
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
    """Yordamchi funksiya: bitta studentning bitta achievement bo'yicha progressi"""
    ach = await get_achievement_by_id(db, achievement_id)
    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalar_one_or_none()

    if not ach or not student:
        return 0

    if ach.criteria_type == "project_count":
        res = await db.execute(
            select(func.count(Project.id)).where(Project.student_id == student_id, Project.status == "Approved"))
        current = res.scalar() or 0
    else:
        current = student.total_points

    return min(100, int((current / max(ach.criteria_value, 1)) * 100))


async def get_achievement_statistics(db: AsyncSession, achievement_id: int) -> dict:
    """Achievement bo'yicha umumiy statistika"""
    ach = await get_achievement_by_id(db, achievement_id)
    if not ach: return {}

    earned_count_res = await db.execute(
        select(func.count(StudentAchievement.id)).where(StudentAchievement.achievement_id == achievement_id))
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


# ========== CRUD (CREATE / UPDATE / DELETE) ==========

async def create_achievement(db: AsyncSession, **kwargs) -> Achievement:
    new_achievement = Achievement(**kwargs)
    db.add(new_achievement)
    await db.commit()
    await db.refresh(new_achievement)
    return new_achievement


async def update_achievement(db: AsyncSession, achievement_id: int, **kwargs) -> Optional[Achievement]:
    achievement = await get_achievement_by_id(db, achievement_id)
    if not achievement: return None
    for key, value in kwargs.items():
        if value is not None: setattr(achievement, key, value)
    await db.commit()
    await db.refresh(achievement)
    return achievement


async def delete_achievement(db: AsyncSession, achievement_id: int) -> bool:
    achievement = await get_achievement_by_id(db, achievement_id)
    if not achievement: return False
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


async def check_course_completion(db: AsyncSession, student_id: int, course_id: int) -> bool:
    return True


async def award_certificate(db: AsyncSession, student_id: int, course_id: int):
    # 1. Avval berilganligini tekshirish
    existing = await db.execute(
        select(CourseCertificate).where(
            and_(CourseCertificate.student_id == student_id, CourseCertificate.course_id == course_id)
        )
    )
    if existing.scalar_one_or_none():
        print("⚠️ Sertifikat allaqachon mavjud")
        return None

    # 2. To'liq tugatganini tekshirish
    is_complete = await check_course_completion(db, student_id, course_id)
    print(f"✅ is_complete: {is_complete}")
    if not is_complete:
        print("❌ Kurs tugatilmagan")
        return None

    # 3. Sertifikat yaratish
    new_cert = CourseCertificate(
        student_id=student_id,
        course_id=course_id,
        issued_at=datetime.utcnow()
    )
    db.add(new_cert)

    student_res = await db.execute(select(Student).where(Student.id == student_id))
    student = student_res.scalar_one_or_none()
    if student:
        student.total_points += 500

    await db.commit()
    await db.refresh(new_cert)
    print(f"🎉 Sertifikat yaratildi: {new_cert.id}")
    return new_cert


async def get_my_certificates(db: AsyncSession, student_id: int):
    """Talabaning sertifikatlarini kurs ma'lumotlari bilan olish"""
    result = await db.execute(
        select(CourseCertificate)
        .options(selectinload(CourseCertificate.course))
        .where(CourseCertificate.student_id == student_id)
    )
    return result.scalars().all()


async def get_course_certified_students(db: AsyncSession, course_id: int):
    """Muayyan kursdan sertifikat olgan barcha talabalar"""
    result = await db.execute(
        select(CourseCertificate)
        .options(selectinload(CourseCertificate.student))
        .where(CourseCertificate.course_id == course_id)
    )
    certs = result.scalars().all()
    return [
        {
            "student_name": c.student.full_name or c.student.username,
            "issued_at": c.issued_at,
            "certificate_id": c.id
        } for c in certs
    ]


async def get_course_certificate(
    db: AsyncSession, student_id: int, course_id: int
) -> Optional[CourseCertificate]:
    result = await db.execute(
        select(CourseCertificate)
        .options(selectinload(CourseCertificate.course))
        .where(
            and_(
                CourseCertificate.student_id == student_id,
                CourseCertificate.course_id == course_id,
            )
        )
    )
    cert = result.scalar_one_or_none()
    print(f"🔍 get_course_certificate: student={student_id}, course={course_id}, cert={cert}")
    return cert

async def generate_certificate_pdf(
        db: AsyncSession, student_id: int, achievement_id: int
) -> Optional[Union[io.BytesIO, str]]:
    # 1. Talaba achievement olganini tekshirish
    sa_result = await db.execute(
        select(StudentAchievement)
        .options(selectinload(StudentAchievement.achievement))
        .where(
            and_(
                StudentAchievement.student_id == student_id,
                StudentAchievement.achievement_id == achievement_id,
            )
        )
    )
    student_achievement = sa_result.scalar_one_or_none()
    if not student_achievement:
        print(f"❌ Student {student_id} achievement {achievement_id} olmagan")
        return None

    student_res = await db.execute(select(Student).where(Student.id == student_id))
    student = student_res.scalar_one_or_none()
    if not student:
        print(f"❌ Student {student_id} topilmadi")
        return None

    achievement = student_achievement.achievement

    try:
        pdf_buffer = generate_badge_certificate(
            student_name=student.full_name or student.username,
            achievement_name=achievement.name,
            achievement_description=achievement.description,
            cert_number=student_achievement.id,
        )
        print(f"✅ PDF yaratildi: {pdf_buffer}")
        return pdf_buffer
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return "error"
