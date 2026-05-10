import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

async def check():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = [t[0] for t in res.fetchall()]
        
        for table in tables:
            res = await conn.execute(text(f"""
                SELECT conname, confdeltype 
                FROM pg_constraint c 
                JOIN pg_class cl ON cl.oid = c.conrelid
                JOIN pg_namespace n ON n.oid = c.connamespace 
                WHERE n.nspname = 'public' AND cl.relname = '{table}'
            """))
            rows = res.fetchall()
            for row in rows:
                if row[1] == b'a': # NO ACTION
                    print(f"NO ACTION: Table: {table}, Constraint: {row[0]}")

asyncio.run(check())
