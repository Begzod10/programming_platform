from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.user import Student
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password, create_access_token
from app.db.session import get_db
from fastapi import APIRouter, Depends, Query
from app.db.base_class import Base


async def register_new_student(db: AsyncSession, user_data: UserCreate):
    result = await db.execute(select(Student).where(Student.email == user_data.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email bilan ro'yxatdan o'tilgan."
        )

    hashed_pass = get_password_hash(user_data.password)
    new_student = Student(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_pass,
    )

    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)
    return new_student


async def login(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(Student).where(Student.email == email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email yoki parol noto'g'ri"
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email yoki parol noto'g'ri"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Foydalanuvchi faol emas"
        )

    access_token = create_access_token(subject=user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


async def logout(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(Student).where(Student.email == email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email yoki parol noto'g'ri"
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email yoki parol noto'g'ri"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Foydalanuvchi faol emas"
        )

    return {"message": "Logout qilindi"}


async def get_current_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.id == user_id))
    user = result.scalars().first()
    return user


async def get_current_active_user(current_user: Student = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Foydalanuvchi faol emas"
        )
    return current_user


async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )
    await db.delete(user)
    await db.commit()
    return {"message": "Foydalanuvchi o'chirildi"}


async def update_user(user_id: int, user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )

    user.username = user_data.username
    user.email = user_data.email
    user.full_name = user_data.full_name
    user.hashed_password = get_password_hash(user_data.password)

    await db.commit()
    await db.refresh(user)
    return user


async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student))
    users = result.scalars().all()
    return users
