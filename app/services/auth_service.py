from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.user import Student
<<<<<<< Updated upstream
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password, create_access_token
<<<<<<< HEAD
=======
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
>>>>>>> Stashed changes
from app.db.session import get_db
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
=======
>>>>>>> origin/branch-shoh


async def register_new_student(db: AsyncSession, user_data: UserCreate):
    # Email tekshirish
    result = await db.execute(select(Student).where(Student.email == user_data.email))
    if result.scalars().first():
<<<<<<< Updated upstream
        raise HTTPException(status_code=400, detail="Bu email bilan ro'yxatdan o'tilgan.")

    result2 = await db.execute(select(Student).where(Student.username == user_data.username))
    if result2.scalars().first():
        raise HTTPException(status_code=400, detail="Bu username band!")
=======
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email bilan ro'yxatdan o'tilgan."
        )

    result2 = await db.execute(select(Student).where(Student.username == user_data.username))
    if result2.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu username band."
        )
>>>>>>> Stashed changes

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
    # OAuth2PasswordRequestForm "username" field yuboradi
    # shuning uchun email sifatida qabul qilamiz
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )
    await db.delete(user)
    await db.commit()
    return {"message": "Foydalanuvchi o'chirildi"}


<<<<<<< Updated upstream
# ✅ UserUpdate ishlatadi — faqat ruxsat etilgan maydonlarni o'zgartiradi
async def update_user(user_id: int, user_data: UserUpdate, db: AsyncSession):
=======
async def update_user(user_id: int, user_data: UserCreate, db: AsyncSession):
>>>>>>> Stashed changes
    result = await db.execute(select(Student).where(Student.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )

    for key, value in user_data.dict(exclude_unset=True).items():
        if value is not None:
            setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
<<<<<<< HEAD
    return user


async def get_users(db: AsyncSession):
    result = await db.execute(select(Student))
    return result.scalars().all()


async def get_current_student(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token yaroqsiz yoki muddati o'tgan",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    result = await db.execute(select(Student).where(Student.id == user_id))
    student = result.scalars().first()
    if student is None:
        raise credentials_exception
    return student
=======
    return user
>>>>>>> origin/branch-shoh
