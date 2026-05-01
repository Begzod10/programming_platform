from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.models.user import UserRole


# --- ACHIEVEMENT SCHEMAS ---
class AchievementRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    badge_image_url: Optional[str] = None
    points_reward: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- USER SCHEMAS ---
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = Field(default=UserRole.student)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username kamida 3 ta belgi bo'lishi kerak")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 5:
            raise ValueError("Parol kamida 5 ta belgi bo'lishi kerak")
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    @field_validator("username", "full_name", "bio")
    @classmethod
    def strip_strings(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else v


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr

    # Optional maydonlar: bazada null bo'lsa default qiymat oladi
    full_name: Optional[str] = Field(default=None)
    bio: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)

    # Role: Agar bazada kutilmagan rol yoki bo'sh (NULL) bo'lsa xato bermasligi uchun
    role: UserRole

    @field_validator("role", mode="before")
    @classmethod
    def set_default_role(cls, v):
        if v == UserRole.teacher or v == "teacher":
            return UserRole.teacher
        return UserRole.student

    # Default qiymatlar bilan himoyalash
    current_level: Optional[str] = Field(default="Beginner")
    total_points: int = Field(default=0)
    is_active: bool = Field(default=True)
    phone: Optional[str] = Field(default=None)
    balance: int = Field(default=0)
    surname: Optional[str] = Field(default=None)
    created_at: datetime

    # Yutuqlar: agar relationship yuklanmagan bo'lsa bo'sh list qaytadi
    achievements: List[AchievementRead] = Field(default_factory=list)

    # Pydantic v2 uchun sozlama
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


# --- AUTH SCHEMAS ---
class UserLogin(BaseModel):
    username: str
    password: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead