import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.course import Course

async def delete_test():
    engine = create_async_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as db:
        try:
            course = await db.execute(select(Course).where(Course.id == 2))
            c = course.scalar_one_or_none()
            if c:
                await db.delete(c)
                await db.commit()
                print("Deleted successfully")
            else:
                print("Course not found")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(delete_test())
