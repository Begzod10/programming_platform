import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app import settings

async def reset_database():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        # Barcha jadvallarni va sxemani o'chirish (pgAdmin-siz)
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
        print("Baza toliq tozalandi!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(reset_database())