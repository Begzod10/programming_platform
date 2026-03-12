<<<<<<< HEAD
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.user import Student
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Student:
    """
    JWT tokendan user_id oladi va DB dan studentni qaytaradi.
    Token noto'g'ri yoki muddati o'tgan bo'lsa → 401
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token noto'g'ri yoki muddati o'tgan",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)
    if not user_id:
        raise credentials_exception
=======
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import AsyncSessionLocal
from app.config import settings
from app.models.user import Student


# ✅ Yagona get_db — barcha fayllar shu yerdan import qilsin
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ✅ get_current_student bu yerda — project_service.py dan ko'chirildi
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_student(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> Student:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: int = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token noto'g'ri yoki muddati o'tgan",
            headers={"WWW-Authenticate": "Bearer"},
        )
>>>>>>> origin/branch-shoh

    result = await db.execute(select(Student).where(Student.id == user_id))
    user = result.scalars().first()

    if not user:
<<<<<<< HEAD
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Student = Depends(get_current_user),
) -> Student:
    """
    Foydalanuvchi aktiv ekanini tekshiradi.
    is_active=False bo'lsa → 403
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Foydalanuvchi faol emas",
        )
    return current_user


async def get_current_verified_user(
    current_user: Student = Depends(get_current_active_user),
) -> Student:
    """
    Foydalanuvchi tasdiqlangan ekanini tekshiradi.
    is_verified=False bo'lsa → 403
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Foydalanuvchi tasdiqlanmagan",
        )
    return current_user


# SAHIFALASH PARAMETRLARI Endpointlarda qayta ishlatish uchun:  pagination: dict = Depends(get_pagination)

def get_pagination(
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """
    Sahifalash uchun offset va limit hisoblaydi.

    Qaytaradi:
        { "page": 1, "page_size": 10, "offset": 0, "limit": 10 }
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Sahifa raqami 1 dan kichik bo'lmasligi kerak",
        )
    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Sahifa hajmi 1 dan 100 gacha bo'lishi kerak",
        )
    offset = (page - 1) * page_size
    return {
        "page": page,
        "page_size": page_size,
        "offset": offset,
        "limit": page_size,
    }
=======
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Foydalanuvchi faol emas")

    return user
>>>>>>> origin/branch-shoh
