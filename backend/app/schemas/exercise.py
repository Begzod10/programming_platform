from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime


class ExerciseCreate(BaseModel):
    title: str
    description: str
    exercise_type: str = "text_input"  # fill_in_blank | drag_and_drop | multiple_choice | text_input

    # Fill in blank
    correct_answers: Optional[str] = None  # "javob1,javob2"

    # Drag and drop
    drag_items: Optional[str] = None      # JSON: ["item1","item2"]
    correct_order: Optional[str] = None   # JSON: ["item2","item1"]

    # Multiple choice
    options: Optional[str] = None         # JSON: ["A variant","B variant","C variant"]
    is_multiple_select: bool = False

    # Text input
    expected_answer: Optional[str] = None

    # Umumiy
    hint: Optional[str] = None
    explanation: Optional[str] = None
    difficulty_level: str = "Easy"
    points: int = 10
    order: int = 0


class ExerciseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    exercise_type: Optional[str] = None
    correct_answers: Optional[str] = None
    drag_items: Optional[str] = None
    correct_order: Optional[str] = None
    options: Optional[str] = None
    is_published: Optional[bool] = None  # ← shu qatorni qo'shing
    is_multiple_select: Optional[bool] = None
    expected_answer: Optional[str] = None
    hint: Optional[str] = None
    explanation: Optional[str] = None
    difficulty_level: Optional[str] = None
    points: Optional[int] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class ExerciseRead(BaseModel):
    id: int
    lesson_id: int
    title: str
    description: str
    exercise_type: str
    drag_items: Optional[str] = None
    options: Optional[str] = None
    is_multiple_select: bool
    hint: Optional[str] = None
    difficulty_level: str
    points: int
    order: int
    is_published: bool = False
    is_active: bool
    created_at: datetime
    # correct_answers, expected_answer, correct_order — studentga ko'rsatilmaydi!
    model_config = ConfigDict(from_attributes=True)


class ExerciseSubmitRequest(BaseModel):
    student_answer: str  # JSON string yoki oddiy matn


class ExerciseSubmissionRead(BaseModel):
    id: int
    exercise_id: int
    student_id: int
    student_answer: str
    is_correct: Optional[bool] = None
    score: Optional[int] = None
    ai_feedback: Optional[str] = None
    submitted_at: datetime
    model_config = ConfigDict(from_attributes=True)




class ExerciseReorderRequest(BaseModel):
    exercise_id_1: int
    exercise_id_2: int