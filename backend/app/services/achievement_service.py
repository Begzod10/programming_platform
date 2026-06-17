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
from app.models.dictionary import UserDictionary
from sqlalchemy import and_

import io
from app.utils.certificate import generate_certificate, generate_badge_certificate
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Union


FULLSTACK_NAME = "Full Stack Developer"
FULLSTACK_DESC = (
    "Platformadagi barcha kurslarni muvaffaqiyatli tugatdingiz — Full Stack "
    "Developer darajasiga erishdingiz."
)
FULLSTACK_POINTS_REWARD = 500
FULLSTACK_BADGE_URL = "/static/badges/fullstack.svg"


# Course title → badge slug. Match is case-insensitive substring on the
# course title; first hit wins. Patterns are ordered most-specific first
# so 'react' doesn't get clobbered by a hypothetical 'r' pattern.
_COURSE_BADGE_PATTERNS = [
    ("react",        "react"),
    ("postgres",     "sql"),
    ("sql",          "sql"),
    ("telegram",     "telegram"),
    ("aiogram",      "telegram"),
    ("github",       "git"),
    ("git",          "git"),
    ("flask",        "python"),
    ("django",       "python"),
    ("python",       "python"),
    ("javascript",   "javascript"),
    (" js ",         "javascript"),
    ("html",         "html-css"),
    ("css",          "html-css"),
    ("dasturlash",   "intro"),
    ("asoslar",      "intro"),
    ("kirish",       "intro"),
]


def _badge_url_for_course_title(title: str) -> str:
    """Map a course title to its bundled badge URL, or '' if no rule fits."""
    if not title:
        return ""
    needle = f" {title.lower()} "
    for pattern, slug in _COURSE_BADGE_PATTERNS:
        if pattern in needle:
            return f"/static/badges/{slug}.svg"
    return ""


# URLs known to be placeholder values from earlier seed data — we treat
# these as "no badge" and overwrite when a real one is available.
_PLACEHOLDER_BADGE_URLS = {"", "/static/default_badge.png"}


async def _backfill_course_badge_urls(db: AsyncSession) -> int:
    """Walk course-completion achievements with empty/placeholder badge URLs
    and set them to the matching bundled badge based on the course title.
    Returns the number of rows updated. Idempotent."""
    from app.models.course import Course

    res = await db.execute(
        select(Achievement, Course.title)
        .outerjoin(Course, Course.id == Achievement.course_id)
        .where(Achievement.criteria_type == "course_completion")
    )
    updated = 0
    for ach, course_title in res.all():
        existing = (ach.badge_image_url or "").strip()
        if existing not in _PLACEHOLDER_BADGE_URLS:
            continue
        url = _badge_url_for_course_title(course_title or ach.name)
        if not url or url == existing:
            continue
        ach.badge_image_url = url
        updated += 1
    if updated:
        await db.commit()
    return updated


async def _get_or_create_fullstack_achievement(db: AsyncSession) -> Achievement:
    """Return the single platform-wide 'Full Stack Developer' Achievement row.

    Deduplicates on every call: if multiple rows with criteria_type=
    'all_courses_completed' exist (from earlier double-inserts), keep the
    lowest-id one and delete the rest so the achievements page never shows
    duplicate cards.
    """
    res = await db.execute(
        select(Achievement)
        .where(Achievement.criteria_type == "all_courses_completed")
        .order_by(Achievement.id)
    )
    rows = res.scalars().all()

    if len(rows) > 1:
        # Keep the first, delete the duplicates
        keeper = rows[0]
        for dup in rows[1:]:
            # Re-point any student_achievements at the keeper before deletion
            from app.models.student_achievement import StudentAchievement as SA
            await db.execute(
                SA.__table__.update()
                .where(SA.__table__.c.achievement_id == dup.id)
                .values(achievement_id=keeper.id)
            )
            await db.delete(dup)
        await db.commit()
        await db.refresh(keeper)
        existing = keeper
    elif len(rows) == 1:
        existing = rows[0]
    else:
        existing = None

    if existing is not None:
        if not (existing.badge_image_url or "").strip():
            existing.badge_image_url = FULLSTACK_BADGE_URL
            await db.commit()
            await db.refresh(existing)
        return existing

    ach = Achievement(
        name=FULLSTACK_NAME,
        description=FULLSTACK_DESC,
        badge_image_url=FULLSTACK_BADGE_URL,
        points_reward=FULLSTACK_POINTS_REWARD,
        criteria_type="all_courses_completed",
        criteria_value=0,
        course_id=None,
    )
    db.add(ach)
    await db.commit()
    await db.refresh(ach)
    return ach


async def _all_published_courses_complete(db: AsyncSession, student_id: int) -> bool:
    """True iff the student holds a CourseCertificate for every published
    + active course that has at least one active lesson. Courses with no
    active lessons can't be completed and are skipped so a stub course
    doesn't block the badge."""
    from app.models.course import Course

    course_res = await db.execute(
        select(Course.id).where(
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
            CourseCertificate.student_id == student_id
        )
    )
    held = {r[0] for r in cert_res.all()}
    return required_ids.issubset(held)


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

    # Make sure the Full-Stack achievement row exists so the check below sees
    # it on first run. Idempotent.
    await _get_or_create_fullstack_achievement(db)
    # Auto-attach bundled badge URLs to any course-completion achievement
    # row that still points at a placeholder. Idempotent and cheap (one
    # SELECT + an UPDATE only when a row actually changes).
    await _backfill_course_badge_urls(db)

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
        elif ach.criteria_type == "all_courses_completed":
            if await _all_published_courses_complete(db, student_id):
                should_award = True
        elif ach.criteria_type == "lesson_count":
            lc_res = await db.execute(
                select(func.count(LessonCompletion.id)).where(
                    LessonCompletion.student_id == student_id
                )
            )
            completed_lessons = lc_res.scalar() or 0
            if completed_lessons >= ach.criteria_value:
                should_award = True
        elif ach.criteria_type == "word_count":
            wc_res = await db.execute(
                select(func.count(UserDictionary.id)).where(
                    UserDictionary.student_id == student_id
                )
            )
            saved_words = wc_res.scalar() or 0
            if saved_words >= ach.criteria_value:
                should_award = True
        elif ach.criteria_type == "course_count":
            cc_res = await db.execute(
                select(func.count(CourseCertificate.id)).where(
                    CourseCertificate.student_id == student_id
                )
            )
            certs_count = cc_res.scalar() or 0
            if certs_count >= ach.criteria_value:
                should_award = True

        if should_award:
            # For "all_courses_completed", bonus = sum of the student's actual
            # approved project points so the reward reflects their real effort.
            bonus_points = None
            if ach.criteria_type == "all_courses_completed":
                pts_res = await db.execute(
                    select(func.sum(Project.points_earned)).where(
                        Project.student_id == student_id,
                        Project.status == "Approved",
                        Project.points_earned > 0,
                    )
                )
                bonus_points = int(pts_res.scalar() or 0)

            result = await award_achievement(db, student_id, ach.id, bonus_points=bonus_points)
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

    # 4. Enroll the student in the next course by display_order.
    try:
        from app.models.course import Course, student_courses as sc_table
        course_res = await db.execute(select(Course).where(Course.id == course_id))
        current_course = course_res.scalar_one_or_none()
        if current_course:
            next_res = await db.execute(
                select(Course)
                .where(
                    Course.display_order > current_course.display_order,
                    Course.is_active == True,
                    Course.is_published == True,
                )
                .order_by(Course.display_order)
                .limit(1)
            )
            next_course = next_res.scalar_one_or_none()
            if next_course:
                already_res = await db.execute(
                    select(sc_table.c.course_id).where(
                        sc_table.c.course_id == next_course.id,
                        sc_table.c.student_id == student_id,
                    )
                )
                if already_res.first() is None:
                    await db.execute(
                        sc_table.insert().values(
                            student_id=student_id, course_id=next_course.id
                        )
                    )
                    await db.commit()
                    print(
                        f"🔓 Keyingi kurs ochildi: student={student_id}, "
                        f"course={next_course.id} ({next_course.title})"
                    )
    except Exception as e:
        print(f"⚠️  Next-course unlock failed for student={student_id}: {e}")

    # 5. Did this just complete the whole platform? If so, mint the
    # Full-Stack Developer achievement immediately — no need to wait for
    # the next periodic check_and_award sweep.
    try:
        if await _all_published_courses_complete(db, student_id):
            fullstack = await _get_or_create_fullstack_achievement(db)
            await award_achievement(db, student_id, fullstack.id)
    except Exception as e:
        # Failing the bonus award must never roll back the course certificate.
        print(f"⚠️  Fullstack check failed for student={student_id}: {e}")

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


async def award_achievement(
    db: AsyncSession,
    student_id: int,
    achievement_id: int,
    bonus_points: Optional[int] = None,
) -> Optional[StudentAchievement]:
    """Studentga achievement berish, ball qo'shish va course_id ni bog'lash.

    bonus_points: if provided, overrides achievement.points_reward (used for
    all_courses_completed to reward the student's actual project points total).
    """
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
    points_to_add = bonus_points if bonus_points is not None else achievement.points_reward
    from app.services.ranking_service import RankingService
    ranking_service = RankingService(db)
    await ranking_service.add_points_to_student(student_id, points_to_add)

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
