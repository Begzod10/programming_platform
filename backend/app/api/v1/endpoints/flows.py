from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db, get_current_teacher
from app.schemas.flow import FlowRead
from app.services.flow_service import FlowService
from app.models.user import Student

router = APIRouter()


@router.get("/", response_model=List[FlowRead])
async def get_flows(
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_teacher)
):
    """Faqat o'qituvchiga tegishli flow'lar (turon-only — see app/models/flow.py)"""
    service = FlowService(db)
    return await service.get_all_flows(teacher_id=current_user.id)
