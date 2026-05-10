import asyncio
from app.db.database import AsyncSessionLocal
from app.models.user import Student
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Student.username))
        items = res.scalars().all()
        for i in items:
            print(f"Username: {i}")

if __name__ == "__main__":
    asyncio.run(check())
