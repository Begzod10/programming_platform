from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from app.schemas.exercise import ExerciseRead
from datetime import datetime


class LessonBase(BaseModel):
    """Lesson base schema"""
    title: str = Field(..., min_length=1, max_length=200, description="Dars nomi")
    order: int = Field(default=0, ge=0, description="Dars tartibi")

    # ✅ VAZIFA FIELD'LARI - YANGI
    task_title: Optional[str] = Field(None, max_length=200, description="Vazifa sarlavhasi")
    task_description: Optional[str] = Field(None, description="Vazifa tavsifi")
    task_requirements: Optional[str] = Field(None, description="Talablar (har qatordan)")
    task_technologies: Optional[str] = Field(None, description="Texnologiyalar (vergul bilan)")
    task_deadline_days: Optional[int] = Field(None, ge=1, le=365, description="Muddat (kunlarda)")

    # Kontent
    text_content: Optional[str] = Field(None, description="Matn kontenti")
    code_content: Optional[str] = Field(None, description="Kod kontenti")
    code_language: Optional[str] = Field(None, max_length=50, description="Dasturlash tili")
    video_url: Optional[str] = Field(None, max_length=500, description="Video URL")
    image_url: Optional[str] = Field(None, max_length=500, description="Rasm URL")
    file_url: Optional[str] = Field(None, max_length=500, description="Fayl URL")
    project_id: Optional[int] = Field(None, ge=1, description="Proyekt ID")


class LessonCreate(LessonBase):
    """Yangi dars yaratish"""

    @field_validator("code_language")
    @classmethod
    def validate_code_language(cls, v: Optional[str]) -> Optional[str]:
        """Dasturlash tilini tekshirish"""
        if v:
            allowed_languages = [
                "python", "javascript", "typescript", "java", "c++", "csharp",
                "go", "rust", "php", "ruby", "swift", "kotlin", "html", "css"
            ]
            if v.lower() not in allowed_languages:
                raise ValueError(
                    f"Dasturlash tili quyidagilardan biri bo'lishi kerak: {', '.join(allowed_languages)}"
                )
            return v.lower()
        return v


class LessonUpdate(BaseModel):
    """Darsni yangilash (barcha fieldlar optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    order: Optional[int] = Field(None, ge=0)

    # ✅ VAZIFA - YANGI
    task_title: Optional[str] = Field(None, max_length=200)
    task_description: Optional[str] = None
    task_requirements: Optional[str] = None
    task_technologies: Optional[str] = None
    task_deadline_days: Optional[int] = Field(None, ge=1, le=365)

    # Kontent
    text_content: Optional[str] = None
    code_content: Optional[str] = None
    code_language: Optional[str] = Field(None, max_length=50)
    video_url: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = Field(None, max_length=500)
    file_url: Optional[str] = Field(None, max_length=500)
    project_id: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.schemas.exercise import ExerciseRead


class LessonRead(LessonBase):
    id: int
    course_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    exercises: List["ExerciseRead"] = []
    is_completed: bool = False  # ✅ qo'shildi
    model_config = ConfigDict(from_attributes=True)


class LessonListResponse(BaseModel):
    """Darslar ro'yxati response"""
    lessons: list[LessonRead]
    total: int
    course_id: int


class LessonImageUploadResponse(BaseModel):
    """Rasm yuklash response"""
    message: str
    image_url: str
    lesson: LessonRead


class LessonTaskRead(BaseModel):
    """Faqat vazifa ma'lumotlari"""
    id: int
    title: str
    task_title: Optional[str]
    task_description: Optional[str]
    task_requirements: Optional[str]
    task_technologies: Optional[str]
    task_deadline_days: Optional[int]

    model_config = ConfigDict(from_attributes=True)
