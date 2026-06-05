from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class LessonFeedbackIn(BaseModel):
    """Payload from student when submitting/updating lesson feedback."""
    rating: int = Field(..., ge=1, le=5, description="1-5 yulduz")
    comment: Optional[str] = Field(
        None, max_length=2000, description="Talaba izohi (ixtiyoriy)"
    )


class LessonFeedbackOut(BaseModel):
    """Student's own feedback for prefill."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    lesson_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    updated_at: datetime


class LessonFeedbackComment(BaseModel):
    """One comment shown to the teacher in the dashboard."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    updated_at: datetime
    student_id: int
    student_name: Optional[str] = None


class LessonFeedbackSummary(BaseModel):
    """Per-lesson aggregate row for the teacher dashboard."""
    lesson_id: int
    lesson_title: str
    lesson_order: int
    response_count: int
    average_rating: Optional[float]
    rating_breakdown: dict  # {"1": 0, "2": 1, ...}


class CourseFeedbackOverview(BaseModel):
    """Whole-course overview returned to teachers/admins."""
    course_id: int
    course_title: str
    total_responses: int
    average_rating: Optional[float]
    lessons: List[LessonFeedbackSummary]
