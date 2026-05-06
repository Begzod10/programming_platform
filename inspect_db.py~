import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

async def inspect_db():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        print("Tables in public schema:")
        res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = res.fetchall()
        for t in tables:
            print(f"- {t[0]}")
            res_cols = await conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name='{t[0]}'"))
            cols = res_cols.fetchall()
            print(f"  Columns: {[c[0] for c in cols]}")

if __name__ == "__main__":
    asyncio.run(inspect_db())
