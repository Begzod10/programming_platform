import asyncio
from sqlalchemy import text
from app.db.database import engine

async def add_teacher_id_column():
    async with engine.begin() as conn:
        try:
            # Check if column exists
            result = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='groups' AND column_name='teacher_id'"))
            if not result.fetchone():
                print("Adding teacher_id column to groups table...")
                await conn.execute(text("ALTER TABLE groups ADD COLUMN teacher_id INTEGER REFERENCES students(id) ON DELETE SET NULL"))
                print("Column added successfully.")
            else:
                print("Column teacher_id already exists.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(add_teacher_id_column())
