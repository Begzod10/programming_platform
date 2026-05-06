from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_student
from app.schemas.user import UserCreate, UserRead, TokenResponse, UserUpdate, UserLogin
from app.services import auth_service
from app.models.user import Student

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    return await auth_service.register_new_student(db, user_in)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
        user_in: UserLogin,
        db: AsyncSession = Depends(get_db)
):
    return await auth_service.login(db, user_in.username, user_in.password)


@router.post(
    "/logout",
    summary="Logout user"
)
async def logout():
    """
    Tizimdan chiqish

    JWT token client tomonda saqlanadi, shuning uchun logout
    client tomonida token'ni o'chirish orqali amalga oshiriladi.
    """
    return {
        "message": "Logout muvaffaqiyatli",
        "detail": "Token'ni client tomonida o'chiring (localStorage yoki sessionStorage)"
    }


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user info"
)
async def get_me(
        current_student: Student = Depends(get_current_student)
):
    """Joriy foydalanuvchi ma'lumotlarini olish"""
    return current_student


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_me(
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    return await auth_service.delete_user(current_student.id, db)


@router.put("/me", status_code=status.HTTP_200_OK)
async def update_me(
        user_data: UserUpdate,
        current_student: Student = Depends(get_current_student),
        db: AsyncSession = Depends(get_db)
):
    return await auth_service.update_user(current_student.id, user_data, db)
