from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.user import UserRead


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class GroupRead(GroupBase):
    id: int
    created_at: datetime
    students: List[UserRead] = []

    class Config:
        from_attributes = True