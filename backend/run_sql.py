import asyncio
from app.db.database import engine
from sqlalchemy import text

async def run_migration():
    sql1 = """
    CREATE TABLE IF NOT EXISTS student_groups (
        student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
        group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE,
        PRIMARY KEY (student_id, group_id)
    );
    """
    
    sql2 = """
    INSERT INTO student_groups (student_id, group_id)
    SELECT id, group_id FROM students 
    WHERE group_id IS NOT NULL
    ON CONFLICT (student_id, group_id) DO NOTHING;
    """
    
    try:
        async with engine.begin() as conn:
            await conn.execute(text(sql1))
            print("Table `student_groups` created or already exists.")
            
            result = await conn.execute(text(sql2))
            print(f"Data copied successfully. Inserted/Ignored rows.")
            
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    asyncio.run(run_migration())
