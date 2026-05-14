import asyncio
from sqlalchemy import text
from app import engine

async def check_duplicate():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT id, username, email FROM students WHERE email='rimefara_teach@gennis.uz'"))
        rows = result.fetchall()
        print(f"Found {len(rows)} rows:")
        for r in rows:
            print(f"ID: {r[0]}, Username: {r[1]}, Email: {r[2]}")

if __name__ == "__main__":
    asyncio.run(check_duplicate())
