"""Teacher-only maintenance endpoint for the in-memory translation store.

Request handlers read RU text only from `translation_store`, which is loaded once at startup. Content built by a
separate process (scripts/build_course.py) writes `translation_cache` rows the running service has never seen;
this reloads them without a restart.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_instructor, get_db
from app.models.user import Student
from app.services import translation_store as ts

router = APIRouter()


@router.post("/translations/reload")
async def reload_translations(
        db: AsyncSession = Depends(get_db),
        _teacher: Student = Depends(get_current_instructor),
):
    await ts.load(db)
    return {"entries": len(ts._store)}
