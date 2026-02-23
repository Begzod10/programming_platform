from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.user import UserRead
from app.models.user import Student

router = APIRouter()


@router.get("/", response_model=List[UserRead])
async def get_students(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        search: str = Query(None),
        db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select, or_

    query = select(Student)

    if search:
        query = query.where(
            or_(
                Student.username.ilike(f"%{search}%"),
                Student.full_name.ilike(f"%{search}%"),
                Student.email.ilike(f"%{search}%")
            )
        )

    result = await db.execute(
        query.offset(skip).limit(limit)
    )
    students = result.scalars().all()

    return students