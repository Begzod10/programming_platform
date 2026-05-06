from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List
from datetime import datetime


class CourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    description: str = Field(..., min_length=1)
    difficulty_level: str
    duration_weeks: int = Field(..., ge=1)
    max_points: int = Field(..., ge=0)
    prerequisite_course_id: Optional[int] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_intro_url: Optional[str] = None
    syllabus_url: Optional[str] = None

    @field_validator("difficulty_level")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        allowed = ["Beginner", "Intermediate", "Advanced", "Expert"]
        if v not in allowed:
            raise ValueError(f"Ruxsat etilgan: {', '.join(allowed)}")
        return v


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[str] = None
    duration_weeks: Optional[int] = None
    max_points: Optional[int] = None
    is_active: Optional[bool] = None
    is_published: Optional[bool] = None
    prerequisite_course_id: Optional[int] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
<<<<<<< HEAD:app/schemas/course.py
=======
    video_intro_url: Optional[str] = None
    syllabus_url: Optional[str] = None
>>>>>>> 6302b1b38cd53ccc73e4ac391c43b986a66e6d1d:backend/app/schemas/course.py


class CourseRead(CourseBase):
    id: int
    instructor_id: int
    instructor_name: Optional[str] = None
    is_active: bool
    is_published: bool
    created_at: datetime
    updated_at: datetime
    progress_percentage: int = 0
    lessons_count: int = 0
    students_count: int = 0
    prerequisite_course_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class CourseReadWithStudents(CourseRead):
    pass


class CourseImageUploadResponse(BaseModel):
    message: str
    image_url: str
