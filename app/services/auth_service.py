from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.models.user import Student, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def create_ranking(db: AsyncSession, student_id: int):
    """Ranking yaratish helper function"""
    from app.models.ranking import Ranking

    # Mavjudligini tekshirish
    result = await db.execute(select(Ranking).where(Ranking.student_id == student_id))
    if result.scalar_one_or_none():
        return None

    # Yangi ranking yaratish
    new_ranking = Ranking(
        student_id=student_id,
        daily_points=0,
        weekly_points=0,
        monthly_points=0,
        total_points=0,
        global_rank=0,
        level_rank=0,
        projects_completed=0,
        average_grade=0.0
    )
    db.add(new_ranking)
    await db.commit()
    await db.refresh(new_ranking)
    return new_ranking


async def register_new_student(db: AsyncSession, user_data: UserCreate):
    """Yangi foydalanuvchi ro'yxatdan o'tkazish"""
    # Email tekshirish
    result = await db.execute(select(Student).where(Student.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Bu email bilan ro'yxatdan o'tilgan."
        )

    # Username tekshirish
    result2 = await db.execute(select(Student).where(Student.username == user_data.username))
    if result2.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Bu username band!"
        )

    # Yangi foydalanuvchi yaratish
    new_student = Student(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
    )
    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)

    # ✅ Ranking avtomatik yaratish (FAQAT student uchun)
    if new_student.role == UserRole.student:
        await create_ranking(db, new_student.id)

    # Token yaratish
    access_token = create_access_token(subject=new_student.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_student
    }


async def login(db: AsyncSession, username: str, password: str):
    """Login - username YOKI email bilan"""
    username = username.strip()
    result = await db.execute(
        select(Student).where(
            (Student.username == username) |
            (Student.email == username)
        )
    )
    user = result.scalars().first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username yoki parol noto'g'ri"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Foydalanuvchi faol emas"
        )

    # ✅ Teacher login qilganda avtomatik sync
    if user.role == UserRole.teacher:
        try:
            from app.api.v1.endpoints.classroom import sync_students_internal
            await sync_students_internal(db)
        except Exception as e:
            print(f"Sync xatosi: {e}")  # Sync xato bo'lsa login to'xtamasin

    return {
        "access_token": create_access_token(subject=user.id),
        "token_type": "bearer",
        "user": user
    }


async def logout(db: AsyncSession, email: str, password: str):
    """Logout (TODO: Redis token blacklist)"""
    return {"message": "Logout qilindi"}


async def delete_user(user_id: int, db: AsyncSession):
    """Foydalanuvchini o'chirish"""
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


async def update_user(user_id: int, user_data: UserUpdate, db: AsyncSession):
    """Foydalanuvchini yangilash"""
    result = await db.execute(select(Student).where(Student.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi"
        )

    # Ma'lumotlarni yangilash
    for key, value in user_data.dict(exclude_unset=True).items():
        if value is not None:
            setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return user


async def get_current_student(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
):
    """Token'dan foydalanuvchini olish"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token yaroqsiz yoki muddati o'tgan",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Token'ni decode qilish
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    # Foydalanuvchini topish
    result = await db.execute(select(Student).where(Student.id == user_id))
    student = result.scalars().first()

    if student is None:
        raise credentials_exception

    return student