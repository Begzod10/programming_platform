from typing import AsyncGenerator, Optional, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import AsyncSessionLocal
from app.config import settings
from app.models.user import Student, UserRole


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


from app.core.security import decode_access_token


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
    return result.scalars().first()


async def get_current_student(
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


# Aliases for compatibility
get_current_user = get_current_student
get_current_teacher = get_current_instructor
