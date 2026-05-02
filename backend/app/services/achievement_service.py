from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.achievement import Achievement
from app.models.student_achievement import StudentAchievement
from app.models.user import Student
from app.models.project import Project
from typing import Optional, List
from datetime import datetime
from app.models.lesson import Lesson, LessonCompletion
from app.models.submission import Submission
from app.models.student_achievement import CourseCertificate
from sqlalchemy import and_

import io
from app.utils.certificate import generate_certificate, generate_badge_certificate
from sqlalchemy.ext.asyncio import AsyncSession
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

async def revoke_achievement(db: AsyncSession, student_id: int, achievement_id: int) -> bool:
    """Studentdan achievementni qaytib olish"""
    result = await db.execute(
        select(StudentAchievement).where(
            StudentAchievement.student_id == student_id,
            StudentAchievement.achievement_id == achievement_id
        )
    )
    student_achievement = result.scalar_one_or_none()
    if not student_achievement:
        return False

    achievement = await get_achievement_by_id(db, achievement_id)
    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalar_one_or_none()

    if student and achievement:
        from app.services.ranking_service import RankingService
        ranking_service = RankingService(db)
        await ranking_service.subtract_points_from_student(student_id, achievement.points_reward)

    await db.delete(student_achievement)
    await db.commit()
    return True


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

    achievements = await get_all_achievements(db)

    awarded = []
    for ach in achievements:
        should_award = False
        if ach.criteria_type == "project_count" and completed_projects >= ach.criteria_value:
            should_award = True
        elif ach.criteria_type == "points_threshold" and student.total_points >= ach.criteria_value:
            should_award = True
        elif ach.criteria_type == "course_completion" and ach.course_id:
            # Kurs tugatilganini tekshiramiz
            is_complete = await check_course_completion(db, student_id, ach.course_id)
            if is_complete:
                should_award = True

        if should_award:
            result = await award_achievement(db, student_id, ach.id)
            if result:
                awarded.append(result)
            
            # AGAR BU KURS SERTIFIKATI BO'LSA - Rasmiy sertifikatni ham beramiz
            if ach.criteria_type == "course_completion" and ach.course_id:
                await award_certificate(db, student_id, ach.course_id)
                
    return awarded


# ========== COURSE COMPLETION & CERTIFICATE ==========

async def check_course_completion(db: AsyncSession, student_id: int, course_id: int) -> bool:
    """Studentning kursni to'liq tugatganini tekshirish — LessonCompletion orqali"""

    # 1. Kursda nechta aktiv dars bor
    total_res = await db.execute(
        select(func.count(Lesson.id)).where(
            Lesson.course_id == course_id,
            Lesson.is_active == True
        )
    )
    total = total_res.scalar() or 0

    if total == 0:
        return False

    # 2. Student nechta darsni tugatgan
    completed_res = await db.execute(
        select(func.count(LessonCompletion.id))
        .select_from(LessonCompletion)
        .join(Lesson, LessonCompletion.lesson_id == Lesson.id)
        .where(
            Lesson.course_id == course_id,
            LessonCompletion.student_id == student_id
        )
    )
    completed = completed_res.scalar() or 0

    return completed >= total


async def award_certificate(
    db: AsyncSession, student_id: int, course_id: int
) -> Optional[CourseCertificate]:
    """Kursning barcha darslari tugaganda avtomatik sertifikat berish.
    Allaqachon sertifikat mavjud bo'lsa yoki kurs tugatilmagan bo'lsa None qaytaradi."""

    # 1. Sertifikat allaqachon berilganmi?
    existing_res = await db.execute(
        select(CourseCertificate).where(
            and_(
                CourseCertificate.student_id == student_id,
                CourseCertificate.course_id == course_id,
            )
        )
    )
    if existing_res.scalar_one_or_none():
        print(f"ℹ️ Sertifikat allaqachon mavjud: student={student_id}, course={course_id}")
        return None

    # 2. Kurs to'liq tugatilganmi?
    is_complete = await check_course_completion(db, student_id, course_id)
    if not is_complete:
        return None

    # 3. Yangi sertifikat yaratish
    cert = CourseCertificate(student_id=student_id, course_id=course_id)
    db.add(cert)
    await db.commit()
    await db.refresh(cert)
    print(f"🎓 Sertifikat berildi: student={student_id}, course={course_id}, cert_id={cert.id}")
    return cert


async def check_course_prerequisite(
    db: AsyncSession, student_id: int, course_id: int
) -> bool:
    """Kursning oldingi kursi tugatilganmi tekshiradi.
    True  → kirish ruxsat beriladi (prereq yo'q yoki tugatilgan)
    False → kirish bloklanadi (prereq tugatilmagan)"""
    from app.models.course import Course

    # Kursni olish
    course_res = await db.execute(select(Course).where(Course.id == course_id))
    course = course_res.scalar_one_or_none()

    if not course:
        return False  # Kurs topilmadi

    # Prereq yo'q bo'lsa — hamma kirishi mumkin
    if not course.prerequisite_course_id:
        return True

    # Prereq kursni talaba tugatganmi?
    return await check_course_completion(db, student_id, course.prerequisite_course_id)


async def award_achievement(db: AsyncSession, student_id: int, achievement_id: int) -> Optional[StudentAchievement]:
    """Studentga achievement berish, ball qo'shish va course_id ni bog'lash"""
    # 1. Avval berilganini tekshirish
    existing = await db.execute(
        select(StudentAchievement).where(
            StudentAchievement.student_id == student_id,
            StudentAchievement.achievement_id == achievement_id
        )
    )
    if existing.scalar_one_or_none():
        return None

    # 2. Ma'lumotlarni olish
    achievement = await get_achievement_by_id(db, achievement_id)
    student_result = await db.execute(select(Student).where(Student.id == student_id))
    student = student_result.scalar_one_or_none()

    if not student or not achievement:
        return None

    # 3. Balllarni yangilash (Ranking bilan birga)
    from app.services.ranking_service import RankingService
    ranking_service = RankingService(db)
    await ranking_service.add_points_to_student(student_id, achievement.points_reward)

    # 4. Bazaga yozish (course_id bilan birga)
    new_sa = StudentAchievement(
        student_id=student_id,
        achievement_id=achievement_id,
        course_id=achievement.course_id,  # Muhim: frontend uchun
        earned_at=datetime.utcnow()
    )
    db.add(new_sa)

    # 5. Saqlash
    await db.commit()
    await db.refresh(new_sa)
    return new_sa


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
    """Achievement uchun badge PDF yaratish"""
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


# ========== MONITORING & PROGRESS ==========

async def get_achievement_progress(db: AsyncSession, student_id: int) -> List[dict]:
    """Studentning barcha achievementlar bo'yicha progressini hisoblash"""
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
        if ach.criteria_type == "project_count":
            current = completed_projects
        elif ach.criteria_type == "course_completion" and ach.course_id:
            # Kurs progressini hisoblaymiz
            current = 1 if await check_course_completion(db, student_id, ach.course_id) else 0
        else:
            current = student.total_points

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
