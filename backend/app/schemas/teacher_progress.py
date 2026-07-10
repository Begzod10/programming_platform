from datetime import datetime
from typing import List, Optional, Any

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class TeacherStudentCourseProgress(BaseModel):
    course_id: int
    course_title: str
    difficulty_level: str
    progress_percentage: float = Field(ge=0, le=100)
    completed_lessons: int
    total_lessons: int
    earned_points: int
    max_points: int
    is_completed: bool
    model_config = ConfigDict(from_attributes=True)


class TeacherStudentProgress(BaseModel):
    student_id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    balance: int = 0
    current_level: str
    total_points: int
    global_rank: Optional[int] = None
    courses_count: int
    average_progress: float = Field(ge=0, le=100)
    courses: List[TeacherStudentCourseProgress] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class TeacherStudentProgressList(BaseModel):
    total: int
    page: int = 1
    size: int = 10
    total_pages: int = 1
    items: List[TeacherStudentProgress]
    model_config = ConfigDict(from_attributes=True)


class TeacherStudentProgressDetail(TeacherStudentProgress):
    enrollment_date: datetime
    created_at: datetime
    is_active: bool


class TeacherStudentRanking(BaseModel):
    student_id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    current_level: str
    total_points: int
    # Points for the selected period (== total_points when period is 'all').
    # Surfaced so the FE can render the bar relative to the visible window
    # instead of lifetime totals.
    period_points: int = 0
    global_rank: Optional[int] = None
    current_course: Optional[str] = None
    best_course: Optional[str] = None
    best_course_points: int = 0
    model_config = ConfigDict(from_attributes=True)


class TeacherStudentRankingList(BaseModel):
    total: int
    period: str = "all"
    items: List[TeacherStudentRanking]
    model_config = ConfigDict(from_attributes=True)
