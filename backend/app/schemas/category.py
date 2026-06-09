from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=80)


class CategoryRead(CategoryBase):
    id: int
    slug: str
    courses_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
