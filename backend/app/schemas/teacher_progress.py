from datetime import datetime
from typing import List, Optional, Any

from pydantic import BaseModel, ConfigDict, Field, EmailStr, HttpUrl


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
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
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
