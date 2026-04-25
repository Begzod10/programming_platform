from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class AchievementBase(BaseModel):
    name: str
    description: str
    badge_image_url: Optional[str] = ""
    points_reward: int
    criteria_type: str  # project_count, points_threshold
    criteria_value: int


class AchievementCreate(AchievementBase):
    @field_validator("name", "description")
    @classmethod
    def strip_strings(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v

    @field_validator("criteria_type")
    @classmethod
    def validate_criteria_type(cls, v: str) -> str:
        allowed = ["project_count", "points_threshold"]
        if v not in allowed:
            raise ValueError(f"criteria_type must be one of: {allowed}")
        return v

    @field_validator("points_reward", "criteria_value")
    @classmethod
    def validate_positive(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Qiymat manfiy bo'lmasligi kerak")
        return v


class AchievementUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    badge_image_url: Optional[str] = None
    points_reward: Optional[int] = None
    criteria_type: Optional[str] = None
    criteria_value: Optional[int] = None


class AchievementRead(AchievementBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class StudentAchievementRead(BaseModel):
    id: int
    course_id: Optional[int] = None  # Kurs ID si frontend uchun muhim
    achievement_name: str
    description: str
    badge_image_url: str
    points_reward: int
    earned_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_custom(cls, sa: "StudentAchievement"):
        return cls(
            id=sa.id,
            # Ustun bo'sh bo'lsa, yutuq modelidan oladi
            course_id=sa.course_id or (sa.achievement.course_id if sa.achievement else None),
            achievement_name=sa.achievement.name if sa.achievement else "Noma'lum",
            description=sa.achievement.description if sa.achievement else "",
            badge_image_url=sa.achievement.badge_image_url if sa.achievement else "",
            points_reward=sa.achievement.points_reward if sa.achievement else 0,
            earned_at=sa.earned_at,
        )


class AchievementProgress(BaseModel):
    achievement_id: int
    name: str
    description: str
    badge_image_url: str
    points_reward: int
    criteria_type: str
    criteria_value: int
    current_value: int
    progress: int
    is_earned: bool


# ✅ YANGI - Teacher uchun

class StudentWithAchievementRead(BaseModel):
    """Sertifikat olgan student"""
    student_id: int
    username: str
    full_name: str
    email: str
    earned_at: datetime
    total_points: int
    current_level: str


class StudentWithoutAchievementRead(BaseModel):
    """Sertifikat olmagan student"""
    student_id: int
    username: str
    full_name: Optional[str] = None
    total_points: int
    current_level: str
    progress: int  # Foizda


class AchievementStatistics(BaseModel):
    """Achievement statistikasi"""
    achievement_id: int
    achievement_name: str
    total_students: int
    students_earned: int
    students_not_earned: int
    completion_percentage: float


class CertificateRead(BaseModel):
    id: int
    course_id: int
    course_title: str
    issued_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CertificateDetail(CertificateRead):
    student_id: int
    student_name: Optional[str] = None
    course_difficulty: Optional[str] = None
    course_duration_weeks: Optional[int] = None
