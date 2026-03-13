from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class LessonCreate(BaseModel):
    title: str
    order: int = 0
    text_content: Optional[str] = None
    code_content: Optional[str] = None
    code_language: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    file_url: Optional[str] = None
    project_id: Optional[int] = None


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    order: Optional[int] = None
    text_content: Optional[str] = None
    code_content: Optional[str] = None
    code_language: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    file_url: Optional[str] = None
    project_id: Optional[int] = None
    is_active: Optional[bool] = None


class LessonRead(BaseModel):
    id: int
    course_id: int
    title: str
    order: int
    text_content: Optional[str] = None
    code_content: Optional[str] = None
    code_language: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    file_url: Optional[str] = None
    project_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)