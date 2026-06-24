from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LessonSampleRead(BaseModel):
    id: int
    lesson_id: int
    title: str
    description: Optional[str] = None
    sample_type: str = "web"
    html_code: Optional[str] = None
    css_code: Optional[str] = None
    js_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LessonSampleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    sample_type: str = "web"
    html_code: Optional[str] = None
    css_code: Optional[str] = None
    js_code: Optional[str] = None
