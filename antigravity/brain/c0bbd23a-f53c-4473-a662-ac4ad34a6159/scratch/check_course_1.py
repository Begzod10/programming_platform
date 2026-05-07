import asyncio
from app.db.database import AsyncSessionLocal
from app.models.lesson import Lesson
from app.models.exercise import Exercise
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Lesson.id).where(Lesson.course_id == 1, Lesson.is_active == True))
        l_ids = res.scalars().all()
        if l_ids:
            res = await db.execute(select(Exercise.id).where(Exercise.lesson_id.in_(l_ids), Exercise.is_active == True))
            e_ids = res.scalars().all()
        else:
            e_ids = []
        print(f"Active Lesson IDs: {l_ids}")
        print(f"Active Exercise IDs: {e_ids}")

if __name__ == "__main__":
    asyncio.run(check())
