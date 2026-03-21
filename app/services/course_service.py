from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.course import Course


class CourseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def delete_course(self, course_id: int) -> bool:
        result = await self.db.execute(select(Course).where(Course.id == course_id))
        course = result.scalar_one_or_none()

        if not course:
            return False

        await self.db.delete(course)
        await self.db.commit()
        return True