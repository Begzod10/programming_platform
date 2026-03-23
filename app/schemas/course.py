from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List
from datetime import datetime


class CourseBase(BaseModel):
    """Base course fields"""
    title: str = Field(..., min_length=1, max_length=150)
    description: str = Field(..., min_length=1, max_length=5000)
    difficulty_level: str = Field(..., max_length=20)
    duration_weeks: int = Field(..., ge=1, le=104)
    max_points: int = Field(..., ge=0, le=10000)
    image_url: Optional[str] = Field(None, max_length=500)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    video_intro_url: Optional[str] = Field(None, max_length=500)
    syllabus_url: Optional[str] = Field(None, max_length=500)

    @field_validator("difficulty_level")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        allowed = ["Beginner", "Intermediate", "Advanced", "Expert"]
        if v not in allowed:
            raise ValueError(f"Qiyinlik darajasi: {', '.join(allowed)}")
        return v


class CourseCreate(CourseBase):
    """Kurs yaratish"""
    pass


class CourseUpdate(BaseModel):
    """Kurs yangilash (barcha fieldlar optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, min_length=1, max_length=5000)
    difficulty_level: Optional[str] = Field(None, max_length=20)
    duration_weeks: Optional[int] = Field(None, ge=1, le=104)
    max_points: Optional[int] = Field(None, ge=0, le=10000)
    image_url: Optional[str] = Field(None, max_length=500)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    video_intro_url: Optional[str] = Field(None, max_length=500)
    syllabus_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

    @field_validator("difficulty_level")
    @classmethod
    def validate_difficulty(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = ["Beginner", "Intermediate", "Advanced", "Expert"]
        if v not in allowed:
            raise ValueError(f"Qiyinlik darajasi: {', '.join(allowed)}")
        return v


class CourseRead(BaseModel):
    """Kurs ma'lumotlari (list va detail uchun)"""
    id: int
    title: str
    description: str
    instructor_id: int
    difficulty_level: str
    duration_weeks: int
    max_points: int
    image_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_intro_url: Optional[str] = None
    syllabus_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Hisoblangan fieldlar
    lessons_count: int = 0
    students_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class CourseReadWithStudents(CourseRead):
    """Kurs batafsil (detail page uchun - kelajakda qo'shimcha fieldlar bo'lishi mumkin)"""
    pass


class CourseListResponse(BaseModel):
    """Kurslar ro'yxati response"""
    total: int
    courses: List[CourseRead]


class CourseImageUploadResponse(BaseModel):
    """Rasm yuklash response"""
    message: str
    image_url: str
    course: CourseRead