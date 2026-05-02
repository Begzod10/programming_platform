from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class DegreeBase(BaseModel):
    name: str
    description: str
    level: str
    required_points: int
    required_projects: int
    certificate_template: Optional[str] = ""
    badge_image_url: Optional[str] = ""


class DegreeCreate(DegreeBase):
    @field_validator("name", "description")
    @classmethod
    def strip_strings(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        allowed = ["Beginner", "Intermediate", "Advanced", "Expert"]
        if v not in allowed:
            raise ValueError(f"Level must be one of: {allowed}")
        return v

    @field_validator("required_points", "required_projects")
    @classmethod
    def validate_positive(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Qiymat manfiy bo'lmasligi kerak")
        return v


class DegreeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    level: Optional[str] = None
    required_points: Optional[int] = None
    required_projects: Optional[int] = None
    certificate_template: Optional[str] = None
    badge_image_url: Optional[str] = None


class DegreeRead(DegreeBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class StudentDegreeRead(BaseModel):
    id: int
    degree_name: str
    degree_level: str
    earned_at: datetime
    verification_code: str
    certificate_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class DegreeProgress(BaseModel):
    degree_id: int
    degree_name: str
    level: str
    required_points: int
    current_points: int
    points_progress: int
    required_projects: int
    completed_projects: int
    projects_progress: int
    overall_progress: int
    is_earned: bool


class CertificateVerify(BaseModel):
    valid: bool
    student_name: Optional[str] = None
    username: str
    degree_name: str
    degree_level: str
    earned_at: datetime
    verification_code: str
