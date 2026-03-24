from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings
from sqlalchemy import text

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=True,
)


async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            print("✅ Database connection successful.")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise e