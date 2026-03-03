from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class RankingRead(BaseModel):
    id: int
    student_id: int
    total_points: int
    global_rank: int
    level_rank: int
    projects_completed: int
    average_grade: float
    weekly_points: int
    monthly_points: int
    last_calculated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RankingUpdate(BaseModel):
    total_points: Optional[int] = None
    weekly_points: Optional[int] = None
    monthly_points: Optional[int] = None
    projects_completed: Optional[int] = None


class GlobalLeaderboardItem(BaseModel):
    rank: int
    student_id: int
    username: str
    full_name: Optional[str] = None
    total_points: int
    level: str
    projects_completed: int
    average_grade: float


class WeeklyLeaderboardItem(BaseModel):
    student_id: int
    username: str
    weekly_points: int
    total_points: int


class MonthlyLeaderboardItem(BaseModel):
    student_id: int
    username: str
    monthly_points: int
    total_points: int


class MyRankingRead(BaseModel):
    global_rank: int
    level_rank: int
    total_points: int
    weekly_points: int
    monthly_points: int
    projects_completed: int
    last_calculated_at: Optional[datetime] = None
