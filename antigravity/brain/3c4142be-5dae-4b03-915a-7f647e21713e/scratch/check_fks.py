import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

async def check():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        print("Checking courses FK constraints...")
        res = await conn.execute(text("""
            SELECT conname, confdeltype 
            FROM pg_constraint c 
            JOIN pg_class cl ON cl.oid = c.conrelid
            JOIN pg_namespace n ON n.oid = c.connamespace 
            WHERE n.nspname = 'public' AND cl.relname = 'courses'
        """))
        rows = res.fetchall()
        for row in rows:
            print(f"Constraint: {row[0]}, On Delete: {row[1]}")

asyncio.run(check())
