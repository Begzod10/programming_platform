from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
from app.schemas.user import UserRead


class DifficultyLevel(str, Enum):
    easy = "Easy"
    medium = "Medium"
    hard = "Hard"


class ProjectStatusEnum(str, Enum):
    draft = "Draft"
    submitted = "Submitted"
    under_review = "Under Review"
    approved = "Approved"
    rejected = "Rejected"


class Grade(str, Enum):
    a = "A"
    b = "B"
    c = "C"
    d = "D"
    f = "F"


class ProjectBase(BaseModel):
    title: str
    description: str
    github_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    technologies_used: Optional[list[str]] = None
    difficulty_level: DifficultyLevel

    @field_validator("github_url", "live_demo_url", mode="before")
    @classmethod
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError("URL http:// yoki https:// bilan boshlanishi kerak")
        return v

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Sarlavha kamida 3 ta belgidan iborat bo'lishi kerak")
        if len(v) > 200:
            raise ValueError("Sarlavha 200 ta belgidan oshmasligi kerak")
        return v

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 10:
            raise ValueError("Tavsif kamida 10 ta belgidan iborat bo'lishi kerak")
        return v


class ProjectCreate(ProjectBase):
    project_files: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    github_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    technologies_used: Optional[list[str]] = None
    difficulty_level: Optional[DifficultyLevel] = None
    project_files: Optional[str] = None

    @field_validator("github_url", "live_demo_url", mode="before")
    @classmethod
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError("URL http:// yoki https:// bilan boshlanishi kerak")
        return v


class ProjectRead(BaseModel):
    id: int
    student_id: int
    title: str
    description: str
    github_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    project_files: Optional[str] = None
    technologies_used: Optional[list[str]] = None
    difficulty_level: DifficultyLevel
    status: ProjectStatusEnum
    points_earned: int
    instructor_feedback: Optional[str] = None
    grade: Optional[Grade] = None
    views_count: int
    likes_count: int
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectReadWithStudent(ProjectRead):
    student: UserRead

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    projects: list[ProjectReadWithStudent]
    total: int
    page: int
    page_size: int

    model_config = ConfigDict(from_attributes=True)


class ProjectReview(BaseModel):
    """Instructor tomonidan loyihani baholash"""
    status: ProjectStatusEnum
    grade: Grade
    points_earned: int
    instructor_feedback: Optional[str] = None

    @field_validator("points_earned", mode="before")
    @classmethod
    def validate_points(cls, v: int) -> int:
        if v < 0 or v > 100:
            raise ValueError("Ball 0 dan 100 gacha bo'lishi kerak")
        return v


class ProjectStatusUpdate(BaseModel):
    """Faqat statusni yangilash"""
    status: ProjectStatusEnum


class ProjectDifficultyUpdate(BaseModel):
    """Faqat qiyinlik darajasini yangilash"""
    difficulty_level: DifficultyLevel


class ProjectGrade(BaseModel):
    """Faqat baho va ball berish"""
    grade: Grade
    points_earned: int

    @field_validator("points_earned", mode="before")
    @classmethod
    def validate_points(cls, v: int) -> int:
        if v < 0 or v > 100:
            raise ValueError("Ball 0 dan 100 gacha bo'lishi kerak")
        return v


class ProjectComment(BaseModel):
    """Izoh qoldirish"""
    comment: str

    @field_validator("comment", mode="before")
    @classmethod
    def validate_comment(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Izoh kamida 3 ta belgidan iborat bo'lishi kerak")
        if len(v) > 1000:
            raise ValueError("Izoh 1000 ta belgidan oshmasligi kerak")
        return v


ProjectStatus = ProjectStatusEnum
