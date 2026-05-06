import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_conn(url):
    print(f"Testing {url} ...")
    try:
        engine = create_async_engine(url)
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print(f"✅ Success: {url}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    urls = [
        "postgresql+asyncpg://postgres:123@localhost:5433/student_platform",
        "postgresql+asyncpg://postgres:123@localhost:5432/student_platform",
        "postgresql+asyncpg://postgres:postgres@localhost:5433/student_platform",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/student_platform",
    ]
    for url in urls:
        if await test_conn(url):
            print(f"USE THIS URL: {url}")
            break

if __name__ == "__main__":
    asyncio.run(main())
