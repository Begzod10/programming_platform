from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_student
from app.schemas.user import UserCreate, UserRead, TokenResponse, UserUpdate, UserLogin, SSOLogin
from app.services import auth_service, sso_service
from app.models.user import Student
from app.core.rate_limit import rate_limit

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_db),
        _rl: None = Depends(rate_limit(max_calls=10, window_seconds=60)),
):
    return await auth_service.register_new_student(db, user_in)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
        user_in: UserLogin,
        db: AsyncSession = Depends(get_db),
        _rl: None = Depends(rate_limit(max_calls=20, window_seconds=60)),
):
    return await auth_service.login(db, user_in.username, user_in.password)


@router.post("/sso", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def sso_login(
        body: SSOLogin,
        db: AsyncSession = Depends(get_db),
        _rl: None = Depends(rate_limit(max_calls=20, window_seconds=60)),
):
    """classroom SSO handoff — see docs/CLASSROOM_SSO_FOR_STUDENT_PLATFORM.md.

    Same response shape as /login, so the frontend's post-login handling is
    unchanged; the only difference is what got the caller here.
    """
    return await sso_service.resolve_sso_login(db, body.token)


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
