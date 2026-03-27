from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_student, get_current_instructor
from app.services import achievement_service
from app.schemas.achievement import (
    AchievementCreate, AchievementUpdate, AchievementRead,
    StudentAchievementRead, AchievementProgress,
    StudentWithAchievementRead, StudentWithoutAchievementRead,
    AchievementStatistics
)
from typing import List

router = APIRouter()


# ========== PUBLIC / STUDENT ENDPOINTS ==========

@router.get("/", response_model=List[AchievementRead])
async def get_all_achievements(db: AsyncSession = Depends(get_db)):
    """Barcha achievementlar (public)"""
    return await achievement_service.get_all_achievements(db)


@router.get("/my", response_model=List[StudentAchievementRead])
async def my_achievements(
    current_student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    """Mening achievementlarim"""
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
    current_student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    """Mening progressim"""
    progress = await achievement_service.get_achievement_progress(db, current_student.id)
    if not progress:
        raise HTTPException(status_code=404, detail="Ma'lumot topilmadi")
    return progress


@router.post("/check-and-award")
async def check_and_award(
    current_student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    """Avtomatik achievement tekshirish"""
    awarded = await achievement_service.check_and_award_achievements(db, current_student.id)
    if not awarded:
        return {"message": "Yangi achievement yo'q", "awarded": []}
    return {
        "message": f"{len(awarded)} ta yangi achievement berildi!",
        "awarded": [{"id": a.achievement_id, "earned_at": a.earned_at} for a in awarded]
    }


# ========== TEACHER ENDPOINTS ==========

@router.post("/create", response_model=AchievementRead)
async def create_achievement(
    data: AchievementCreate,
    current_teacher = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Yangi achievement yaratish (teacher only)"""
    return await achievement_service.create_achievement(
        db, data.name, data.description,
        data.badge_image_url, data.points_reward,
        data.criteria_type, data.criteria_value
    )


@router.put("/{achievement_id}", response_model=AchievementRead)
async def update_achievement(
    achievement_id: int,
    data: AchievementUpdate,
    current_teacher = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Achievementni yangilash (teacher only)"""
    achievement = await achievement_service.update_achievement(
        db, achievement_id,
        name=data.name,
        description=data.description,
        badge_image_url=data.badge_image_url,
        points_reward=data.points_reward,
        criteria_type=data.criteria_type,
        criteria_value=data.criteria_value
    )
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement topilmadi")
    return achievement


@router.delete("/{achievement_id}")
async def delete_achievement(
    achievement_id: int,
    current_teacher = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Achievementni o'chirish (teacher only)"""
    result = await achievement_service.delete_achievement(db, achievement_id)
    if not result:
        raise HTTPException(status_code=404, detail="Achievement topilmadi")
    return {"message": "Achievement o'chirildi!"}


@router.post("/award")
async def award_achievement(
    student_id: int = Query(...),
    achievement_id: int = Query(...),
    current_teacher = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Studentga achievement berish (teacher only)"""
    result = await achievement_service.award_achievement(db, student_id, achievement_id)
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Achievement berib bo'lmadi yoki allaqachon mavjud"
        )
    return {"message": "Achievement berildi!", "earned_at": result.earned_at}


# ✅ YANGI - Teacher monitoring endpoints

@router.get("/{achievement_id}/students-with", response_model=List[StudentWithAchievementRead])
async def get_students_with_achievement(
    achievement_id: int,
    current_teacher = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Sertifikat olgan studentlar (teacher only)"""
    students = await achievement_service.get_students_with_achievement(db, achievement_id)
    return students


@router.get("/{achievement_id}/students-without", response_model=List[StudentWithoutAchievementRead])
async def get_students_without_achievement(
    achievement_id: int,
    current_teacher = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Sertifikat olmagan studentlar (teacher only)"""
    students = await achievement_service.get_students_without_achievement(db, achievement_id)
    return students


@router.get("/{achievement_id}/statistics", response_model=AchievementStatistics)
async def get_achievement_statistics(
    achievement_id: int,
    current_teacher = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Achievement statistikasi (teacher only)"""
    stats = await achievement_service.get_achievement_statistics(db, achievement_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Achievement topilmadi")
    return stats