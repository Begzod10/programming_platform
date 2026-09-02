from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, Field, model_validator
from typing import Optional, List, Any
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
    # Role is intentionally NOT exposed on the public registration schema.
    # Caller-supplied roles let any anonymous request register as teacher.
    # auth_service.register_new_student always forces UserRole.student.

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
        if len(v) < 8:
            raise ValueError("Parol kamida 8 ta belgi bo'lishi kerak")
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
    # Deliberately `str`, not `EmailStr`: this is an OUTPUT schema reading
    # back whatever is already in the DB. gennis/turon-synced accounts get a
    # synthetic email (f"{username}@{source}.uz" or whatever the source
    # system's own record holds) that a real person never typed and never
    # confirmed — EmailStr's stricter checks (e.g. rejecting reserved-use
    # domains) can reject values that are already stored, which crashed
    # /auth/login with a 500 for an otherwise-successful login. Format
    # validation belongs on the way in (UserCreate.email), where it protects
    # a real user's own registration — not on the way out, where the account
    # already exists and a synthetic email is a normal, expected shape.
    email: str

    @field_validator("email", mode="before")
    @classmethod
    def clean_email(cls, v):
        if isinstance(v, str):
            return v.replace(" ", "")
        return v

    # Optional maydonlar: bazada null bo'lsa default qiymat oladi
    full_name: Optional[str] = Field(default=None)
    bio: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)

    @field_validator("avatar_url", mode="before")
    @classmethod
    def empty_avatar_to_none(cls, v):
        return v if v else None

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

    # Yutuqlar: ORM dagi `student_achievements` (join jadval) bo'yicha
    # to'plab beriladi. Avval bu maydon `achievements` deb belgilangan edi,
    # lekin Student modelida bu nomda relationship yo'q — natijada UI doim
    # bo'sh list olar edi. Endi `student_achievements` orqali to'plab,
    # nested `Achievement` ma'lumotini chiqaramiz.
    achievements: List[AchievementRead] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def collect_achievements(cls, data: Any) -> Any:
        # `from_attributes=True` rejimida `data` ORM model bo'lishi mumkin.
        try:
            if hasattr(data, "student_achievements") and not isinstance(data, dict):
                joined = getattr(data, "student_achievements", None) or []
                # Sodda dict ko'rinishida qaytaramiz, AchievementRead esa
                # `from_attributes` orqali maydonlarni xaritaga soladi.
                extracted = [getattr(sa, "achievement", None) for sa in joined]
                extracted = [a for a in extracted if a is not None]
                # Pydantic v2 dict update qila olmaydi — yangi dict yasaymiz.
                base = {k: getattr(data, k, None) for k in cls.model_fields.keys()}
                base["achievements"] = extracted
                return base
        except Exception:
            pass
        return data

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


class SSOLogin(BaseModel):
    """POST /auth/sso body — see docs/CLASSROOM_SSO_FOR_STUDENT_PLATFORM.md.

    Bounds are deliberately generous (a real HS256 JWT with these claims
    runs a few hundred characters) but still reject obvious garbage before
    it reaches jwt.decode.
    """
    token: str = Field(..., min_length=20, max_length=4096)


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead