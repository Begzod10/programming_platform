import asyncio
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.student_achievement import StudentAchievement
from app.models.achievement import Achievement

async def fix_achievements():
    async with AsyncSessionLocal() as db:
        # 1. Find all student achievements with NULL course_id
        result = await db.execute(
            select(StudentAchievement)
            .where(StudentAchievement.course_id == None)
        )
        sas = result.scalars().all()
        print(f"🔍 Found {len(sas)} student achievements with NULL course_id")

        updated_count = 0
        for sa in sas:
            # Get the achievement to find its course_id
            ach_result = await db.execute(
                select(Achievement).where(Achievement.id == sa.achievement_id)
            )
            ach = ach_result.scalar_one_or_none()
            
            if ach and ach.course_id:
                sa.course_id = ach.course_id
                updated_count += 1
                print(f"✅ Updating SA id={sa.id}: setting course_id={ach.course_id} (Achievement: {ach.name})")
        
        if updated_count > 0:
            await db.commit()
            print(f"🚀 Successfully updated {updated_count} records.")
        else:
            print("ℹ️ No records needed updating.")

if __name__ == "__main__":
    asyncio.run(fix_achievements())
