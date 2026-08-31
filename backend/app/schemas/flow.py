from pydantic import BaseModel
from datetime import datetime
from typing import List
from app.schemas.user import UserRead


class FlowRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    students: List[UserRead] = []

    class Config:
        from_attributes = True
