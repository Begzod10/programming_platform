from pydantic import BaseModel
from typing import Optional, List


class AIReviewResult(BaseModel):
    grade: str
    points: int
    feedback: str
    strengths: List[str] = []
    improvements: List[str] = []
    summary: str


class AIReviewResponse(BaseModel):
    project_id: int
    ai_review: AIReviewResult
    message: str = "AI tahlil muvaffaqiyatli bajarildi"