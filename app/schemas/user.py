from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username kamida 3 ta belgidan iborat bo'lishi kerak")
        if len(v) > 50:
            raise ValueError("Username 50 ta belgidan oshmasligi kerak")
        return v

    @field_validator("email", "password")
    @classmethod
    def strip_strings(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 8:
            raise ValueError("Parol kamida 8 ta belgidan iborat bo'lishi kerak")
        if len(v) > 72:
            return v[:72]
        return v


class UserLogin(BaseModel):
    username: str
    password: str

    @field_validator("username", "password")
    @classmethod
    def strip_strings(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    @field_validator("full_name", "bio", "avatar_url")
    @classmethod
    def strip_strings(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if isinstance(v, str) and v else v


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    bio: Optional[str] = None  # ← shu
    avatar_url: Optional[str] = None  # ← shu
    current_level: str
    total_points: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserRead


class TokenPayload(BaseModel):
    sub: int
