from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_student, get_current_instructor
from app.services.ranking_service import RankingService
from app.schemas.ranking import LeaderboardItem, MyRankingRead, RankingUpdate
from app.models.user import Student
from typing import List, Literal

router = APIRouter()


# ========== STUDENT ENDPOINTS ==========

@router.get("/leaderboard", response_model=List[LeaderboardItem])
async def get_leaderboard(
        period: Literal["daily", "weekly", "monthly", "all"] = Query("all"),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        level: str = Query(None),
        db: AsyncSession = Depends(get_db)
):
    """Leaderboard - Tanlangan period bo'yicha dinamik o'rin (rank) bilan."""
    service = RankingService(db)
    rankings = await service.get_leaderboard(
        period=period,
        limit=limit,
        offset=offset,
        level=level
    )

    result = []
    for r in rankings:
        # Periodga qarab ochkoni dinamik tanlaymiz
        if period == "all":
            pts = r.total_points
        else:
            pts = getattr(r, f"{period}_points", 0)

        result.append(
            LeaderboardItem(
                rank=r.period_rank,
                student_id=r.student_id,
                username=r.username,
                full_name=r.full_name,
                avatar_url=r.avatar_url,
                points=pts,
                level=r.current_level,
                projects_completed=r.projects_completed
            )
        )
    return result


@router.get("/me", response_model=MyRankingRead)
async def my_ranking(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Foydalanuvchining barcha periodlar bo'yicha shaxsiy o'rinlari"""
    service = RankingService(db)
    r = await service.get_my_ranking(current_student.id)

    if not r:
        # Ranking topilmasa default qiymatlar
        return MyRankingRead(
            global_rank=0,
            daily_rank=0,
            weekly_rank=0,
            monthly_rank=0,
            daily_points=0,
            weekly_points=0,
            monthly_points=0,
            total_points=current_student.total_points,
            projects_completed=0,
            last_calculated_at=None
        )

    # Mapping'dan (dict ko'rinishida) ma'lumotlarni olamiz
    return MyRankingRead(
        global_rank=r['all_rank'],
        daily_rank=r['daily_rank'],
        weekly_rank=r['weekly_rank'],
        monthly_rank=r['monthly_rank'],
        daily_points=r['Ranking'].daily_points,
        weekly_points=r['Ranking'].weekly_points,
        monthly_points=r['Ranking'].monthly_points,
        total_points=r['Ranking'].total_points,
        projects_completed=r['Ranking'].projects_completed,
        last_calculated_at=r['Ranking'].last_calculated_at
    )


@router.get("/my-stats")
async def get_my_stats(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    """Dashboard tepadagi widget (yulduzcha va global rank) uchun"""
    service = RankingService(db)
    ranking_data = await service.get_my_ranking(current_student.id)

    if not ranking_data:
        return {
            "total_points": current_student.total_points,
            "global_rank": "-",
            "projects_completed": 0
        }

    # ranking_data['Ranking'] -> Model obyektiga
    # ranking_data['all_rank'] -> Hisoblangan global o'ringa murojaat
    return {
        "total_points": current_student.total_points,
        "global_rank": f"#{ranking_data['all_rank']}" if ranking_data['all_rank'] > 0 else "-",
        "projects_completed": ranking_data['Ranking'].projects_completed
    }


# ========== INSTRUCTOR (TEACHER) ENDPOINTS ==========

@router.post("/", status_code=201)
async def create_ranking(
        student_id: int = Query(..., description="Student ID"),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Yangi ranking yaratish"""
    service = RankingService(db)
    result = await service.create_ranking(student_id)

    if not result:
        raise HTTPException(
            status_code=400,
            detail="Ranking allaqachon mavjud yoki foydalanuvchi student emas"
        )

    return {"message": "Ranking yaratildi!", "id": result.id, "student_id": result.student_id}


@router.put("/{ranking_id}")
async def update_ranking(
        ranking_id: int,
        data: RankingUpdate,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Ranking ochkolarini va statistikasini qo'lda yangilash"""
    service = RankingService(db)
    result = await service.update_ranking(ranking_id, **data.dict(exclude_unset=True))

    if not result:
        raise HTTPException(status_code=404, detail="Ranking topilmadi")

    return {
        "message": "Ranking yangilandi!",
        "id": result.id,
        "total_points": result.student.total_points
    }


@router.delete("/{ranking_id}", status_code=204)
async def delete_ranking(
        ranking_id: int,
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Rankingni o'chirish"""
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
    """Studentga ball qo'shish"""
    service = RankingService(db)
    result = await service.add_points_to_student(student_id, points)
    if not result:
        raise HTTPException(status_code=404, detail="Student topilmadi")
    return {"message": f"{points} ball qo'shildi!", "total_points": result.total_points}


@router.post("/subtract-points")
async def subtract_points(
        student_id: int = Query(...),
        points: int = Query(..., ge=1),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Studentdan ball ayirish"""
    service = RankingService(db)
    result = await service.subtract_points_from_student(student_id, points)
    if not result:
        raise HTTPException(status_code=404, detail="Student topilmadi")
    return {"message": f"{points} ball ayirildi!", "total_points": result.total_points}


@router.post("/recalculate")
async def recalculate_rankings(
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Barcha reytinglarni qayta hisoblash"""
    service = RankingService(db)
    await service.calculate_and_update_rankings()
    return {"message": "Reytinglar qayta hisoblandi!"}


@router.post("/reset-daily")
async def reset_daily(current_teacher: Student = Depends(get_current_instructor), db: AsyncSession = Depends(get_db)):
    service = RankingService(db)
    await service.reset_daily_points()
    return {"message": "Kunlik ballar nolga tushirildi!"}


@router.post("/reset-weekly")
async def reset_weekly(current_teacher: Student = Depends(get_current_instructor), db: AsyncSession = Depends(get_db)):
    service = RankingService(db)
    await service.reset_weekly_points()
    return {"message": "Haftalik ballar nolga tushirildi!"}


@router.post("/reset-monthly")
async def reset_monthly(current_teacher: Student = Depends(get_current_instructor), db: AsyncSession = Depends(get_db)):
    service = RankingService(db)
    await service.reset_monthly_points()
    return {"message": "Oylik ballar nolga tushirildi!"}


@router.get("/all", response_model=List[MyRankingRead])
async def get_all_rankings(
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
        current_teacher: Student = Depends(get_current_instructor),
        db: AsyncSession = Depends(get_db)
):
    """Barcha rankinglarni ko'rish (Teacher uchun)"""
    service = RankingService(db)
    rankings = await service.get_all_rankings(skip, limit)
    return [
        MyRankingRead(
            global_rank=r.global_rank,
            daily_rank=r.daily_rank,
            weekly_rank=r.weekly_rank,
            monthly_rank=r.monthly_rank,
            daily_points=r.daily_points,
            weekly_points=r.weekly_points,
            monthly_points=r.monthly_points,
            total_points=r.total_points,
            projects_completed=r.projects_completed,
            last_calculated_at=r.last_calculated_at
        )
        for r in rankings
    ]
