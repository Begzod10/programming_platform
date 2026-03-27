from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal
from datetime import datetime


class RankingBase(BaseModel):
    """Ranking base schema"""
    daily_points: int = Field(default=0, ge=0)
    weekly_points: int = Field(default=0, ge=0)
    monthly_points: int = Field(default=0, ge=0)
    total_points: int = Field(default=0, ge=0)
    projects_completed: int = Field(default=0, ge=0)


class RankingCreate(BaseModel):
    """Yangi ranking yaratish"""
    student_id: int = Field(..., ge=1, description="Student ID")


class RankingUpdate(BaseModel):
    """Ranking yangilash (barcha fieldlar optional)"""
    daily_points: Optional[int] = Field(None, ge=0)
    weekly_points: Optional[int] = Field(None, ge=0)
    monthly_points: Optional[int] = Field(None, ge=0)
    total_points: Optional[int] = Field(None, ge=0)
    projects_completed: Optional[int] = Field(None, ge=0)


class RankingRead(BaseModel):
    """Ranking ma'lumotlarini o'qish"""
    id: int
    student_id: int
    daily_points: int
    weekly_points: int
    monthly_points: int
    total_points: int
    global_rank: int
    level_rank: int
    projects_completed: int
    average_grade: float
    last_calculated_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MyRankingRead(BaseModel):
    """O'z ranking ma'lumotlari"""
    global_rank: int
    level_rank: int
    daily_points: int
    weekly_points: int
    monthly_points: int
    total_points: int
    projects_completed: int
    last_calculated_at: Optional[datetime] = None


class LeaderboardItem(BaseModel):
    """Leaderboard item (universal)"""
    rank: int
    student_id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    points: int  # period ga qarab: daily/weekly/monthly/total
    level: str
    projects_completed: int


class GlobalLeaderboardItem(BaseModel):
    """Global leaderboard item (batafsil)"""
    rank: int
    student_id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    total_points: int
    level: str
    projects_completed: int
    average_grade: float


class DailyLeaderboardItem(BaseModel):
    """Kunlik leaderboard item"""
    rank: int
    student_id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    daily_points: int
    total_points: int


class WeeklyLeaderboardItem(BaseModel):
    """Haftalik leaderboard item"""
    rank: int
    student_id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    weekly_points: int
    total_points: int


class MonthlyLeaderboardItem(BaseModel):
    """Oylik leaderboard item"""
    rank: int
    student_id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    monthly_points: int
    total_points: int


class LevelLeaderboardItem(BaseModel):
    """Level bo'yicha leaderboard item"""
    rank: int
    student_id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    total_points: int
    projects_completed: int
    level: str


class AddPointsRequest(BaseModel):
    """Ball qo'shish request"""
    student_id: int = Field(..., ge=1)
    points: int = Field(..., ge=1)


class SubtractPointsRequest(BaseModel):
    """Ball ayirish request"""
    student_id: int = Field(..., ge=1)
    points: int = Field(..., ge=1)


class RankingStatsResponse(BaseModel):
    """Dashboard statistika response"""
    total_points: int
    global_rank: str  # "#1" yoki "-"
    projects_completed: int