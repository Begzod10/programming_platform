"""Course category endpoints.

Categories are globally shared. Listing is open to any authenticated caller
(students need it to render the filter chips); creating, renaming, and
deleting are restricted to teachers. Most category writes happen implicitly
via the course form (auto-create on save), so the explicit POST/PUT/DELETE
here is primarily for the manage-categories modal.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_instructor, get_current_student
from app.models.category import Category
from app.models.course import Course
from app.models.user import Student
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.course_service import resolve_category, _slugify

router = APIRouter()


def _to_read(cat: Category, courses_count: int) -> CategoryRead:
    return CategoryRead(
        id=cat.id,
        name=cat.name,
        slug=cat.slug,
        courses_count=courses_count,
        created_at=cat.created_at,
    )


@router.get("/", response_model=List[CategoryRead])
async def list_categories(
    search: Optional[str] = Query(None, max_length=80),
    current_student: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """List every category with a live course count."""
    stmt = (
        select(Category, func.count(Course.id).label("c_count"))
        .outerjoin(Course, Course.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.name.asc())
    )
    if search:
        stmt = stmt.where(Category.name.ilike(f"%{search.strip()}%"))
    rows = (await db.execute(stmt)).all()
    return [_to_read(cat, count or 0) for cat, count in rows]


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    current_teacher: Student = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Explicit create — usually unnecessary thanks to auto-create on course save."""
    cat_id = await resolve_category(
        db,
        category_id=None,
        category_name=payload.name,
        created_by_id=current_teacher.id,
    )
    await db.commit()

    cat = (await db.execute(select(Category).where(Category.id == cat_id))).scalar_one()
    return _to_read(cat, 0)


@router.put("/{category_id}", response_model=CategoryRead)
async def rename_category(
    category_id: int,
    payload: CategoryUpdate,
    current_teacher: Student = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db),
):
    cat = (
        await db.execute(select(Category).where(Category.id == category_id))
    ).scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "Kategoriya topilmadi")

    new_name = (payload.name or "").strip() if payload.name else ""
    if not new_name:
        raise HTTPException(400, "Nom bo'sh bo'lishi mumkin emas")

    if new_name.lower() != cat.name.lower():
        clash = await db.execute(
            select(Category.id).where(
                func.lower(Category.name) == new_name.lower(),
                Category.id != cat.id,
            )
        )
        if clash.scalar_one_or_none() is not None:
            raise HTTPException(409, "Bu nomli kategoriya allaqachon mavjud")
        cat.name = new_name
        cat.slug = _slugify(new_name)

    await db.commit()
    await db.refresh(cat)

    count_res = await db.execute(
        select(func.count(Course.id)).where(Course.category_id == cat.id)
    )
    return _to_read(cat, count_res.scalar() or 0)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_teacher: Student = Depends(get_current_instructor),
    db: AsyncSession = Depends(get_db),
):
    """Delete a category. Courses keep their data and become uncategorized."""
    cat = (
        await db.execute(select(Category).where(Category.id == category_id))
    ).scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "Kategoriya topilmadi")
    await db.delete(cat)
    await db.commit()
