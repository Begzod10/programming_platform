from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_student, get_current_instructor
from app.services.ranking_service import RankingService
from app.schemas.ranking import LeaderboardItem, MyRankingRead, RankingUpdate, RankingCreate
from app.models.user import Student
from typing import List, Literal

router = APIRouter()


# ========== PUBLIC ENDPOINTS ==========

@router.get("/leaderboard", response_model=List[LeaderboardItem])
async def get_leaderboard(
        period: Literal["daily", "weekly", "monthly", "all"] = Query("all"),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        level: str = Query(None),
        db: AsyncSession = Depends(get_db)
):
    """
    Leaderboard - barcha uchun

    period:
    - daily: Kunlik reyting (daily_points)
    - weekly: Haftalik reyting (weekly_points)
    - monthly: Oylik reyting (monthly_points)
    - all: Hammasi (total_points)
    """
    service = RankingService(db)
    rankings = await service.get_leaderboard(
        period=period,
        limit=limit,
        offset=offset,
        level=level
    )

    return [
        LeaderboardItem(
            rank=index + 1 + offset,
            student_id=r.student_id,
            username=r.student.username,
            full_name=r.student.full_name,
            avatar_url=r.student.avatar_url,
            points=r.get_points_for_period(period),
            level=r.student.current_level.value,
            projects_completed=r.projects_completed
        )
        for index, r in enumerate(rankings)
    ]


@router.get("/me", response_model=MyRankingRead)
async def my_ranking(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Mening statistikam"""
    service = RankingService(db)
    ranking = await service.get_my_ranking(current_student.id)

    if not ranking:
        raise HTTPException(status_code=404, detail="Ranking topilmadi")

    return MyRankingRead(
        global_rank=ranking.global_rank,
        level_rank=ranking.level_rank,
        daily_points=ranking.daily_points,
        weekly_points=ranking.weekly_points,
        monthly_points=ranking.monthly_points,
        total_points=ranking.total_points,
        projects_completed=ranking.projects_completed,
        last_calculated_at=ranking.last_calculated_at
    )


@router.get("/my-stats")
async def get_my_stats(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Dashboard uchun statistika"""
    service = RankingService(db)
    ranking = await service.get_my_ranking(current_student.id)

    if not ranking:
        return {
            "total_points": 0,
            "global_rank": "-",
            "projects_completed": 0
        }

    return {
        "total_points": ranking.total_points,
        "global_rank": f"#{ranking.global_rank}" if ranking.global_rank > 0 else "-",
        "projects_completed": ranking.projects_completed
    }


# ========== TEACHER ENDPOINTS ==========

@router.post("/", status_code=201)
async def create_ranking(
        student_id: int = Query(..., description="Student ID"),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Yangi ranking yaratish (faqat teacher)"""
    service = RankingService(db)
    result = await service.create_ranking(student_id)

    if not result:
        raise HTTPException(
            status_code=400,
            detail="Ranking allaqachon mavjud yoki foydalanuvchi student emas"
        )

    return {
        "message": "Ranking yaratildi!",
        "id": result.id,
        "student_id": result.student_id
    }


@router.put("/{ranking_id}")
async def update_ranking(
        ranking_id: int,
        data: RankingUpdate,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Ranking'ni yangilash (faqat teacher)"""
    service = RankingService(db)

    result = await service.update_ranking(
        ranking_id,
        daily_points=data.daily_points,
        weekly_points=data.weekly_points,
        monthly_points=data.monthly_points,
        total_points=data.total_points,
        projects_completed=data.projects_completed
    )

    if not result:
        raise HTTPException(status_code=404, detail="Ranking topilmadi")

    return {
        "message": "Ranking yangilandi!",
        "id": result.id,
        "student_id": result.student_id,
        "total_points": result.total_points
    }


@router.delete("/{ranking_id}", status_code=204)
async def delete_ranking(
        ranking_id: int,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Ranking'ni o'chirish (faqat teacher)"""
    service = RankingService(db)
    success = await service.delete_ranking(ranking_id)

    if not success:
        raise HTTPException(status_code=404, detail="Ranking topilmadi")

    return None


@router.post("/add-points")
async def add_points(
        student_id: int = Query(...),
        points: int = Query(..., ge=1),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Studentga ball qo'shish (faqat teacher)"""
    service = RankingService(db)
    result = await service.add_points_to_student(student_id, points)

    if not result:
        raise HTTPException(status_code=404, detail="Student topilmadi")

    return {
        "message": f"{points} ball qo'shildi!",
        "student_id": student_id,
        "total_points": result.total_points
    }


@router.post("/subtract-points")
async def subtract_points(
        student_id: int = Query(...),
        points: int = Query(..., ge=1),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Studentdan ball ayirish (faqat teacher)"""
    service = RankingService(db)
    result = await service.subtract_points_from_student(student_id, points)

    if not result:
        raise HTTPException(status_code=404, detail="Student topilmadi")

    return {
        "message": f"{points} ball ayirildi!",
        "student_id": student_id,
        "total_points": result.total_points
    }


@router.post("/recalculate")
async def recalculate_rankings(
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Reytinglarni qayta hisoblash (faqat teacher)"""
    service = RankingService(db)
    await service.calculate_and_update_rankings()
    return {"message": "Reytinglar qayta hisoblandi!"}


@router.post("/reset-daily")
async def reset_daily(
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Kunlik ballarni nolga tushirish (faqat teacher)"""
    service = RankingService(db)
    await service.reset_daily_points()
    return {"message": "Barcha studentlarning kunlik ballari nolga tushirildi!"}


@router.post("/reset-weekly")
async def reset_weekly(
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Haftalik ballarni nolga tushirish (faqat teacher)"""
    service = RankingService(db)
    await service.reset_weekly_points()
    return {"message": "Barcha studentlarning haftalik ballari nolga tushirildi!"}


@router.post("/reset-monthly")
async def reset_monthly(
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Oylik ballarni nolga tushirish (faqat teacher)"""
    service = RankingService(db)
    await service.reset_monthly_points()
    return {"message": "Barcha studentlarning oylik ballari nolga tushirildi!"}


@router.get("/all", response_model=List[MyRankingRead])
async def get_all_rankings(
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Barcha ranking'larni ko'rish (faqat teacher)"""
    service = RankingService(db)
    rankings = await service.get_all_rankings(skip, limit)

    return [
        MyRankingRead(
            global_rank=r.global_rank,
            level_rank=r.level_rank,
            daily_points=r.daily_points,
            weekly_points=r.weekly_points,
            monthly_points=r.monthly_points,
            total_points=r.total_points,
            projects_completed=r.projects_completed,
            last_calculated_at=r.last_calculated_at
        )
        for r in rankings
    ]
