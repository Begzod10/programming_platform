import asyncio
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.course import Course

async def list_courses():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Course))
        courses = result.scalars().all()
        print(f"Total Courses: {len(courses)}")
        for c in courses:
            print(f"ID: {c.id}, Title: {c.title}")

if __name__ == "__main__":
    asyncio.run(list_courses())
