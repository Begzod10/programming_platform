from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.user import Student
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password, create_access_token


async def register_new_student(db: AsyncSession, user_data: UserCreate):
    result = await db.execute(select(Student).where(Student.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Bu email bilan ro'yxatdan o'tilgan.")

    result2 = await db.execute(select(Student).where(Student.username == user_data.username))
    if result2.scalars().first():
        raise HTTPException(status_code=400, detail="Bu username band!")

    new_student = Student(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
    )
    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)

    access_token = create_access_token(subject=new_student.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_student
    }


async def login(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(Student).where(Student.email == email))
    user = result.scalars().first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email yoki parol noto'g'ri"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Foydalanuvchi faol emas"
        )

    return {
        "access_token": create_access_token(subject=user.id),
        "token_type": "bearer",
        "user": user
    }


async def logout(db: AsyncSession, email: str, password: str):
    # TODO: Redis bilan token blacklist qo'shish mumkin
    return {"message": "Logout qilindi"}


async def delete_user(user_id: int, db: AsyncSession):
    result = await db.execute(select(Student).where(Student.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foydalanuvchi topilmadi")
    await db.delete(user)
    await db.commit()
    return {"message": "Foydalanuvchi o'chirildi"}


# ✅ UserUpdate ishlatadi — faqat ruxsat etilgan maydonlarni o'zgartiradi
async def update_user(user_id: int, user_data: UserUpdate, db: AsyncSession):
    result = await db.execute(select(Student).where(Student.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foydalanuvchi topilmadi")

    for key, value in user_data.dict(exclude_unset=True).items():
        if value is not None:
            setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user