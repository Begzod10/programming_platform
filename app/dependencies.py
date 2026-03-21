from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
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


async def get_current_student(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> Student:
    """Get current authenticated student (any role)"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: int = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
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
