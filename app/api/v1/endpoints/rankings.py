from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.services import ranking_service
from app.schemas.ranking import GlobalLeaderboardItem, WeeklyLeaderboardItem, MonthlyLeaderboardItem, MyRankingRead, \
    RankingUpdate
from typing import List

router = APIRouter()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/global", response_model=List[GlobalLeaderboardItem])
async def global_leaderboard(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0),
                             db: AsyncSession = Depends(get_db)):
    rankings = await ranking_service.get_global_leaderboard(db, limit, offset)
    return [GlobalLeaderboardItem(rank=r.global_rank, student_id=r.student_id, username=r.student.username,
                                  full_name=r.student.full_name, total_points=r.total_points,
                                  level=r.student.current_level.value, projects_completed=r.projects_completed,
                                  average_grade=round(r.average_grade, 2)) for r in rankings]


@router.get("/me", response_model=MyRankingRead)
async def my_ranking(student_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    ranking = await ranking_service.get_my_ranking(db, student_id)
    if not ranking:
        raise HTTPException(status_code=404, detail="Ranking topilmadi")
    return MyRankingRead(global_rank=ranking.global_rank, level_rank=ranking.level_rank,
                         total_points=ranking.total_points, weekly_points=ranking.weekly_points,
                         monthly_points=ranking.monthly_points, projects_completed=ranking.projects_completed,
                         last_calculated_at=ranking.last_calculated_at)


@router.get("/weekly", response_model=List[WeeklyLeaderboardItem])
async def weekly_leaderboard(limit: int = Query(10), db: AsyncSession = Depends(get_db)):
    rankings = await ranking_service.get_weekly_leaderboard(db, limit)
    return [WeeklyLeaderboardItem(student_id=r.student_id, username=r.student.username, weekly_points=r.weekly_points,
                                  total_points=r.total_points) for r in rankings]


@router.get("/monthly", response_model=List[MonthlyLeaderboardItem])
async def monthly_leaderboard(limit: int = Query(10), db: AsyncSession = Depends(get_db)):
    rankings = await ranking_service.get_monthly_leaderboard(db, limit)
    return [
        MonthlyLeaderboardItem(student_id=r.student_id, username=r.student.username, monthly_points=r.monthly_points,
                               total_points=r.total_points) for r in rankings]


@router.post("/create")
async def create_ranking(student_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    result = await ranking_service.create_ranking(db, student_id)
    if not result:
        raise HTTPException(status_code=400, detail="Ranking allaqachon mavjud")
    return {"message": "Ranking yaratildi!", "id": result.id}


@router.put("/{ranking_id}")
async def update_ranking(ranking_id: int, data: RankingUpdate, db: AsyncSession = Depends(get_db)):
    result = await ranking_service.update_ranking(db, ranking_id, total_points=data.total_points,
                                                  weekly_points=data.weekly_points, monthly_points=data.monthly_points,
                                                  projects_completed=data.projects_completed)
    if not result:
        raise HTTPException(status_code=404, detail="Ranking topilmadi")
    return {"message": "Ranking yangilandi!", "id": result.id}


@router.delete("/{ranking_id}")
async def delete_ranking(ranking_id: int, db: AsyncSession = Depends(get_db)):
    result = await ranking_service.delete_ranking(db, ranking_id)
    if not result:
        raise HTTPException(status_code=404, detail="Ranking topilmadi")
    return {"message": "Ranking o'chirildi!"}


@router.post("/recalculate")
async def recalculate_rankings(db: AsyncSession = Depends(get_db)):
    await ranking_service.calculate_and_update_rankings(db)
    return {"message": "Rankinglar yangilandi!"}
