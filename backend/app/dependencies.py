from typing import Optional, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.config import settings
from app.models.user import Student, UserRole
from app.core.demo import demo_allows, DEMO_RESTRICTED_DETAIL

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


from app.core.security import decode_access_token


def _enforce_demo_scope(user: Student, request: Request) -> None:
    """A demo account may only call the allow-listed lesson endpoints."""
    if user.is_demo and not demo_allows(request.method, request.url.path):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=DEMO_RESTRICTED_DETAIL,
            headers={"X-Demo-Restricted": "1"},
        )


async def get_current_student_optional(
        request: Request,
        token: Optional[str] = Depends(oauth2_scheme_optional),
        db: AsyncSession = Depends(get_db)
) -> Optional[Student]:
    """Get current student if token provided, else None"""
    
    # 1. Standard token extraction
    if not token:
        # Fallback: manual check for Authorization header
        auth = request.headers.get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1]
    
    if not token:
        return None
    
    user_id = decode_access_token(token)
    if user_id is None:
        return None

    result = await db.execute(select(Student).where(Student.id == user_id))
    user = result.scalars().first()
    if user is not None:
        _enforce_demo_scope(user, request)
    return user


async def get_current_student(
        request: Request,
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> Student:
    """Get current authenticated student (any role)"""
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token noto'g'ri yoki muddati o'tgan",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(Student).where(Student.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Foydalanuvchi topilmadi"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Foydalanuvchi faol emas"
        )

    _enforce_demo_scope(user, request)
    return user


async def get_current_instructor(
        current_user: Student = Depends(get_current_student)
) -> Student:
    """Get current teacher (instructor) - only for teacher role"""
    if current_user.role != UserRole.teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu amal faqat teacher uchun"
        )
    return current_user


async def require_games_unlocked(
    student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
) -> Student:
    """Gate the leisure sections (early-learning, duel) behind today's quota.

    Returns 423 Locked with the current progress so the frontend can render a
    "complete N more lessons" screen. Demo accounts bypass the lock.
    """
    # Only real, non-demo students are gated — teachers/admins previewing the
    # leisure sections and demo visitors bypass the lock.
    if getattr(student, "is_demo", False) or getattr(student, "role", None) != UserRole.student:
        return student
    from app.services import daily_quota_service
    status_ = await daily_quota_service.get_today(db, student.id)
    if not status_.unlocked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "code": "QUOTA_LOCKED",
                "completed": status_.completed,
                "required": status_.remaining + status_.completed,
                "remaining": status_.remaining,
            },
        )
    return student


# Aliases for compatibility
get_current_user = get_current_student
get_current_teacher = get_current_instructor
