import asyncio
from app import AsyncSessionLocal as SessionLocal
from app import Course
from sqlalchemy import select

async def check():
    async with SessionLocal() as db:
        res = await db.execute(select(Course.id, Course.title, Course.image_url))
        courses = res.all()
        for c in courses:
            print(f"ID: {c.id}, Title: {c.title}, Image URL: {c.image_url}")

if __name__ == "__main__":
    asyncio.run(check())
