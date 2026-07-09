import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:123@localhost:5432/Student_Platform"


async def run():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        # Check if column exists
        res = await conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='lessons' AND column_name='content_blocks'"
        ))
        exists = res.fetchone() is not None
        if exists:
            print("content_blocks column already exists. Nothing to do.")
        else:
            await conn.execute(text("ALTER TABLE lessons ADD COLUMN content_blocks JSON DEFAULT '[]'"))
            print("Successfully added content_blocks column!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())
