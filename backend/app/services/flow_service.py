from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy.orm import selectinload
from app.models.flow import Flow


class FlowService:
    """Read-only — unlike Group, Flow has no manual create/update/delete;
    every row here comes from turon-v2 via GennisService.sync_teacher_data /
    sync_student_data. Gennis has no equivalent concept, so this is always
    empty for a gennis-only deployment."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_flows(self, teacher_id: Optional[int] = None):
        """Flow'larni (ixtiyoriy o'qituvchi bo'yicha) ichidagi talabalari bilan birga olish"""
        query = select(Flow).options(selectinload(Flow.students))
        if teacher_id:
            query = query.where(Flow.teacher_id == teacher_id)
        result = await self.db.execute(query)
        return result.scalars().all()
