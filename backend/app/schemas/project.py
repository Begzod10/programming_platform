from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
from app.schemas.user import UserRead


# --- Enums

class DifficultyLevel(str, Enum):
    easy = "Easy"
    medium = "Medium"
    hard = "Hard"


class ProjectStatus(str, Enum):
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


# --- Base

class ProjectBase(BaseModel):
    title: str = "Loyiha"           # ← default qo'shing
    description: str = "—"          # ← default qo'shing
    github_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    technologies_used: Optional[list[str]] = None
    difficulty_level: DifficultyLevel = DifficultyLevel.easy  # ← default

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

    @field_validator("technologies_used", mode="before")
    @classmethod
    def parse_technologies(cls, v):
        if isinstance(v, str):
            return [t.strip() for t in v.split(",") if t.strip()]
        return v


# --- Create

class ProjectCreate(ProjectBase):
    project_files: Optional[str] = None


# --- Update

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


# --- Read

class ProjectRead(BaseModel):
    id: int
    student_id: int
    title: str
    description: str
    github_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    technologies_used: Optional[list[str]] = None
    project_files: Optional[str] = None
    difficulty_level: DifficultyLevel
    status: ProjectStatus
    points_earned: int
    instructor_feedback: Optional[str] = None
    grade: Optional[Grade] = None
    views_count: int
    likes_count: int
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # ✅ shu qo'shiladi
    @field_validator("technologies_used", mode="before")
    @classmethod
    def parse_technologies(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except Exception:
                return [t.strip() for t in v.split(",") if t.strip()]
        return v

    model_config = ConfigDict(from_attributes=True)  # ← eng oxirida




# --- Read with Student

class ProjectReadWithStudent(ProjectRead):
    student: UserRead


# --- List Response

class ProjectListResponse(BaseModel):
    projects: list[ProjectReadWithStudent]
    total: int
    page: int
    page_size: int

    model_config = ConfigDict(from_attributes=True)


# --- Review

class ProjectReview(BaseModel):
    status: ProjectStatus
    grade: Grade
    points_earned: int
    instructor_feedback: Optional[str] = None

    @field_validator("points_earned", mode="before")
    @classmethod
    def validate_points(cls, v: int) -> int:
        if v < 0 or v > 100:
            raise ValueError("Ball 0 dan 100 gacha bo'lishi kerak")
        return