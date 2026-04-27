import asyncio
import asyncpg

async def fix_cascade():
    conn = await asyncpg.connect(
        user="postgres",
        password="123",
        database="student_platform",
        host="localhost"
    )
    queries = [
        "ALTER TABLE projects DROP CONSTRAINT IF EXISTS projects_student_id_fkey",
        "ALTER TABLE projects ADD CONSTRAINT projects_student_id_fkey FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE",
        "ALTER TABLE rankings DROP CONSTRAINT IF EXISTS rankings_student_id_fkey",
        "ALTER TABLE rankings ADD CONSTRAINT rankings_student_id_fkey FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE",
        "ALTER TABLE student_achievements DROP CONSTRAINT IF EXISTS student_achievements_student_id_fkey",
        "ALTER TABLE student_achievements ADD CONSTRAINT student_achievements_student_id_fkey FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE",
        "ALTER TABLE student_degrees DROP CONSTRAINT IF EXISTS student_degrees_student_id_fkey",
        "ALTER TABLE student_degrees ADD CONSTRAINT student_degrees_student_id_fkey FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE",
    ]
    for q in queries:
        try:
            await conn.execute(q)
            print(f"OK: {q[:60]}")
        except Exception as e:
            print(f"XATO: {e}")
    await conn.close()
    print("Hammasi tugadi!")

asyncio.run(fix_cascade())
