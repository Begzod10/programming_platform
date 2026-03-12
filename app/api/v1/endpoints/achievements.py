from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db  # ✅ bir joydan import
from app.services import achievement_service
<<<<<<< HEAD
from app.schemas.achievement import AchievementCreate, AchievementUpdate, AchievementRead, StudentAchievementRead, \
    AchievementProgress
=======
from app.schemas.achievement import (
    AchievementCreate, AchievementUpdate, AchievementRead,
    StudentAchievementRead, AchievementProgress
)
>>>>>>> origin/branch-shoh
from typing import List

router = APIRouter()

<<<<<<< HEAD

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
=======
>>>>>>> origin/branch-shoh


@router.get("/", response_model=List[AchievementRead])
async def get_all_achievements(db: AsyncSession = Depends(get_db)):
    return await achievement_service.get_all_achievements(db)


@router.get("/my", response_model=List[StudentAchievementRead])
async def my_achievements(student_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    achievements = await achievement_service.get_my_achievements(db, student_id)
    return [
<<<<<<< HEAD
        StudentAchievementRead(id=sa.id, achievement_name=sa.achievement.name, description=sa.achievement.description,
                               badge_image_url=sa.achievement.badge_image_url,
                               points_reward=sa.achievement.points_reward, earned_at=sa.earned_at) for sa in
        achievements]
=======
        StudentAchievementRead(
            id=sa.id,
            achievement_name=sa.achievement.name,
            description=sa.achievement.description,
            badge_image_url=sa.achievement.badge_image_url,
            points_reward=sa.achievement.points_reward,
            earned_at=sa.earned_at
        ) for sa in achievements
    ]
>>>>>>> origin/branch-shoh


@router.get("/progress", response_model=List[AchievementProgress])
async def achievement_progress(student_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    progress = await achievement_service.get_achievement_progress(db, student_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Student topilmadi")
    return progress


@router.post("/create", response_model=AchievementRead)
async def create_achievement(data: AchievementCreate, db: AsyncSession = Depends(get_db)):
<<<<<<< HEAD
    return await achievement_service.create_achievement(db, data.name, data.description, data.badge_image_url,
                                                        data.points_reward, data.criteria_type, data.criteria_value)
=======
    return await achievement_service.create_achievement(
        db, data.name, data.description,
        data.badge_image_url, data.points_reward,
        data.criteria_type, data.criteria_value
    )
>>>>>>> origin/branch-shoh


@router.put("/{achievement_id}", response_model=AchievementRead)
async def update_achievement(achievement_id: int, data: AchievementUpdate, db: AsyncSession = Depends(get_db)):
<<<<<<< HEAD
    achievement = await achievement_service.update_achievement(db, achievement_id, name=data.name,
                                                               description=data.description,
                                                               badge_image_url=data.badge_image_url,
                                                               points_reward=data.points_reward,
                                                               criteria_type=data.criteria_type,
                                                               criteria_value=data.criteria_value)
=======
    achievement = await achievement_service.update_achievement(
        db, achievement_id,
        name=data.name, description=data.description,
        badge_image_url=data.badge_image_url,
        points_reward=data.points_reward,
        criteria_type=data.criteria_type,
        criteria_value=data.criteria_value
    )
>>>>>>> origin/branch-shoh
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement topilmadi")
    return achievement


@router.delete("/{achievement_id}")
async def delete_achievement(achievement_id: int, db: AsyncSession = Depends(get_db)):
    result = await achievement_service.delete_achievement(db, achievement_id)
    if not result:
        raise HTTPException(status_code=404, detail="Achievement topilmadi")
    return {"message": "Achievement o'chirildi!"}


@router.post("/award")
<<<<<<< HEAD
async def award_achievement(student_id: int = Query(...), achievement_id: int = Query(...),
                            db: AsyncSession = Depends(get_db)):
=======
async def award_achievement(
        student_id: int = Query(...),
        achievement_id: int = Query(...),
        db: AsyncSession = Depends(get_db)
):
>>>>>>> origin/branch-shoh
    result = await achievement_service.award_achievement(db, student_id, achievement_id)
    if not result:
        raise HTTPException(status_code=400, detail="Achievement berib bo'lmadi yoki allaqachon mavjud")
    return {"message": "Achievement berildi!", "earned_at": result.earned_at}


@router.post("/check-and-award")
async def check_and_award(student_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    awarded = await achievement_service.check_and_award_achievements(db, student_id)
    if not awarded:
        return {"message": "Yangi achievement yo'q", "awarded": []}
<<<<<<< HEAD
    return {"message": f"{len(awarded)} ta yangi achievement berildi!",
            "awarded": [{"id": a.achievement_id, "earned_at": a.earned_at} for a in awarded]}
=======
    return {
        "message": f"{len(awarded)} ta yangi achievement berildi!",
        "awarded": [{"id": a.achievement_id, "earned_at": a.earned_at} for a in awarded]
    }
>>>>>>> origin/branch-shoh
