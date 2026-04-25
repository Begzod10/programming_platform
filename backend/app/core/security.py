from datetime import datetime, timedelta
from typing import Any, Union, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt as _bcrypt

from app.config import settings
from app.db.session import get_db
from app.models.user import Student

ALGORITHM = "HS256"

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_password_hash(password: str) -> str:
    """Parolni hash qilish"""
    password_bytes = password.encode('utf-8')[:72]
    salt = _bcrypt.gensalt()
    hashed = _bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Parolni tekshirish"""
    try:
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return _bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """JWT token yaratish"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[int]:
    """Tokendan user_id olish (robust variant)"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        
        # 1. 'sub' maydoni (FastAPI/Standard)
        user_id = payload.get("sub")
        
        # 2. Boshqa ehtimoliy maydonlar
        if user_id is None:
            user_id = payload.get("id") or payload.get("student_id")
            
        if user_id is None:
            return None
            
        try:
            return int(user_id)
        except (ValueError, TypeError):
            return None
            
    except (JWTError, Exception):
        return None


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> Student:
    """Tokendan joriy userni olish"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token noto'g'ri yoki muddati o'tgan",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Tokenni decode qilish
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    # Database'dan userni olish
    from sqlalchemy import select
    result = await db.execute(select(Student).where(Student.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User faol emas"
        )

    return user


async def get_current_active_user(
        current_user: Student = Depends(get_current_user)
) -> Student:
    """Faqat faol userlarni olish"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User faol emas"
        )
    return current_user
