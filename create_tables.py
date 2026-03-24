import asyncio
from app.db.base_class import Base
from app.models.lesson import Lesson
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings


async def create():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Jadvallar yaratildi!")


asyncio.run(create())
