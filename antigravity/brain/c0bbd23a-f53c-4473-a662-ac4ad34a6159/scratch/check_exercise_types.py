import asyncio
from app.db.database import AsyncSessionLocal
from app.models.exercise import Exercise
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Exercise.id, Exercise.exercise_type))
        items = res.all()
        for i in items:
            print(f"ID: {i[0]}, Type: {i[1]}")

if __name__ == "__main__":
    asyncio.run(check())
