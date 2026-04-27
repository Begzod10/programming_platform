import asyncio
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.achievement import Achievement

async def list_achievements():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Achievement))
        achs = result.scalars().all()
        print(f"Total Achievements: {len(achs)}")
        for ach in achs:
            print(f"ID: {ach.id}, Name: {ach.name}, Course ID: {ach.course_id}")

if __name__ == "__main__":
    asyncio.run(list_achievements())
