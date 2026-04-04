from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db, get_current_student, get_current_instructor
from app.services import achievement_service
from app.schemas.achievement import (
    AchievementCreate, AchievementUpdate, AchievementRead,
    StudentAchievementRead, AchievementProgress,
    StudentWithAchievementRead, StudentWithoutAchievementRead,
    AchievementStatistics
)
from app.models.user import Student

router = APIRouter()


# ========== PUBLIC / STUDENT ENDPOINTS (Talabalar uchun) ==========

@router.get("/", response_model=List[AchievementRead])
async def get_all_achievements(db: AsyncSession = Depends(get_db)):
    """Barcha mavjud achievementlar ro'yxati"""
    return await achievement_service.get_all_achievements(db)


@router.get("/my", response_model=List[StudentAchievementRead])
async def my_achievements(
        current_student=Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Mening qo'lga kiritgan achievementlarim"""
    achievements = await achievement_service.get_my_achievements(db, current_student.id)
    return [
        StudentAchievementRead(
            id=sa.id,
            achievement_name=sa.achievement.name,
            description=sa.achievement.description,
            badge_image_url=sa.achievement.badge_image_url,
            points_reward=sa.achievement.points_reward,
            earned_at=sa.earned_at
        ) for sa in achievements
    ]


@router.get("/progress", response_model=List[AchievementProgress])
async def achievement_progress(
        current_student=Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Yutuqlarga bo'lgan progressim (necha foiz qoldi)"""
    progress = await achievement_service.get_achievement_progress(db, current_student.id)
    if not progress:
        raise HTTPException(status_code=404, detail="Progress ma'lumotlari topilmadi")
    return progress


@router.post("/check-and-award")
async def check_and_award(
        current_student=Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Kriteriyalar bajarilgan bo'lsa, avtomatik yutuqlarni berish"""
    awarded = await achievement_service.check_and_award_achievements(db, current_student.id)
    if not awarded:
        return {"message": "Yangi achievement yo'q", "awarded": []}
    return {
        "message": f"{len(awarded)} ta yangi achievement berildi!",
        "awarded": [{"id": a.achievement_id, "earned_at": a.earned_at} for a in awarded]
    }


# ========== TEACHER ENDPOINTS (Faqat o'qituvchilar uchun) ==========

@router.post("/create", response_model=AchievementRead)
async def create_achievement(
        data: AchievementCreate,
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Yangi achievement yaratish (masalan: 'Top Coder')"""
    return await achievement_service.create_achievement(db, **data.model_dump())


@router.put("/{achievement_id}", response_model=AchievementRead)
async def update_achievement(
        achievement_id: int,
        data: AchievementUpdate,
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Achievement ma'lumotlarini tahrirlash"""
    achievement = await achievement_service.update_achievement(
        db, achievement_id, **data.model_dump(exclude_unset=True)
    )
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement topilmadi")
    return achievement


@router.delete("/{achievement_id}")
async def delete_achievement(
        achievement_id: int,
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Achievementni o'chirish (Kaskadli: barcha talabalardan ham o'chadi)"""
    result = await achievement_service.delete_achievement(db, achievement_id)
    if not result:
        raise HTTPException(status_code=404, detail="Achievement topilmadi")
    return {"message": "Achievement muvaffaqiyatli o'chirildi!"}


@router.post("/award")
async def award_achievement(
        student_id: int = Query(...),
        achievement_id: int = Query(...),
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Studentga qo'lda achievement berish (Ball qo'shiladi va Daraja yangilanadi)"""
    result = await achievement_service.award_achievement(db, student_id, achievement_id)
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Achievement berib bo'lmadi yoki studentda u allaqachon mavjud"
        )
    return {"message": "Achievement berildi!", "earned_at": result.earned_at}


@router.delete("/{achievement_id}/revoke")
async def revoke_achievement(
        achievement_id: int,
        student_id: int = Query(...),
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Studentdan achievementni qaytib olish (Ball ayiriladi va Daraja tushishi mumkin)"""
    result = await achievement_service.revoke_achievement(db, student_id, achievement_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Talabada ushbu achievement topilmadi"
        )
    return {"message": "Achievement bekor qilindi, ballar va daraja qayta hisoblandi."}


# ========== MONITORING ENDPOINTS (Statistika) ==========

@router.get("/{achievement_id}/students-with", response_model=List[StudentWithAchievementRead])
async def get_students_with_achievement(
        achievement_id: int,
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Ushbu yutuqni qo'lga kiritgan talabalar ro'yxati"""
    return await achievement_service.get_students_with_achievement(db, achievement_id)


@router.get("/{achievement_id}/students-without", response_model=List[StudentWithoutAchievementRead])
async def get_students_without_achievement(
        achievement_id: int,
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Ushbu yutuqni hali olmagan talabalar va ularning progressi"""
    return await achievement_service.get_students_without_achievement(db, achievement_id)


@router.get("/{achievement_id}/statistics", response_model=AchievementStatistics)
async def get_achievement_statistics(
        achievement_id: int,
        current_teacher=Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Achievement bo'yicha umumiy statistika (foizlar va sonlar)"""
    stats = await achievement_service.get_achievement_statistics(db, achievement_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Statistika topilmadi")
    return stats


@router.post("/fix-levels-all-students")
async def fix_levels(db: AsyncSession = Depends(get_db)):
    """Barcha talabalarning darajasini ballariga qarab to'g'rilab chiqish"""
    result = await db.execute(select(Student))
    students = result.scalars().all()

    updated_count = 0
    for student in students:
        old_level = student.current_level
        student.update_level_based_on_points()
        if old_level != student.current_level:
            updated_count += 1

    await db.commit()
    return {"message": f"{len(students)} ta talabadan {updated_count} tasining darajasi yangilandi."}


@router.post("/force-update-all-levels")
async def force_update_all_levels(db: AsyncSession = Depends(get_db)):
    """Bazadagi barcha studentlarni ballariga qarab darajasini to'g'rilash"""
    # 1. Barcha studentlarni bazadan olamiz
    result = await db.execute(select(Student))
    students = result.scalars().all()

    updated_count = 0
    for student in students:
        old_level = student.current_level
        student.total_points = student.total_points

        if old_level != student.current_level:
            updated_count += 1

    await db.commit()
    return {"status": "Success", "updated_students": updated_count}