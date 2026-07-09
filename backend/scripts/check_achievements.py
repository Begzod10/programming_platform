import asyncio
import os
import sys

# Set path to include app directory
sys.path.append(os.getcwd())

from app.db.database import AsyncSessionLocal
from app.models.achievement import Achievement
from app.models.course import Course
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        print("--- Courses ---")
        res = await db.execute(select(Course.id, Course.title))
        for r in res.all():
            print(f"ID: {r[0]}, Title: {r[1]}")
        
        print("\n--- Achievements ---")
        res = await db.execute(select(Achievement.id, Achievement.name, Achievement.criteria_type, Achievement.course_id))
        for r in res.all():
            print(f"ID: {r[0]}, Name: {r[1]}, Type: {r[2]}, CourseID: {r[3]}")

if __name__ == "__main__":
    asyncio.run(check())
