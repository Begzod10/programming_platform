from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List, Any
from datetime import datetime
from app.models.team_game import GameType, SessionStatus, QuestionStatus


class TeamMemberRead(BaseModel):
    id:         int
    student_id: int
    full_name:  Optional[str] = None
    username:   Optional[str] = None
    avatar_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class GameTeamRead(BaseModel):
    id:      int
    name:    str
    color:   str
    score:   int
    members: List[TeamMemberRead] = []
    model_config = ConfigDict(from_attributes=True)


class GameSessionRead(BaseModel):
    id:                  int
    title:               str
    description:         Optional[str]      = None
    game_type:           GameType
    status:              SessionStatus
    language:            str               = 'uz'
    course_id:           Optional[int]      = None
    course_title:        Optional[str]      = None
    created_by:          int
    team_count:          int
    teams:               List[GameTeamRead]  = []
    created_at:          datetime
    updated_at:          datetime
    my_team_id:          Optional[int]      = None
    current_question_id: Optional[int]      = None
    model_config = ConfigDict(from_attributes=True)


class StudentRead(BaseModel):
    id:         int
    full_name:  Optional[str] = None
    username:   Optional[str] = None
    avatar_url: Optional[str] = None
    group_id:   Optional[int] = None
    group_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class TeamAssignmentItem(BaseModel):
    team_id:     int
    student_ids: List[int]


class StartSessionBody(BaseModel):
    student_ids: Optional[List[int]] = None


class GameSessionCreate(BaseModel):
    title:       str           = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    game_type:   GameType
    course_id:   Optional[int] = None
    team_count:  int           = Field(2, ge=2, le=10)


class ScoreUpdate(BaseModel):
    team_id: int
    delta:   int = Field(..., ge=-10000, le=10000, description="Points to add (positive) or subtract (negative)")

    @field_validator("delta")
    @classmethod
    def delta_nonzero(cls, v: int) -> int:
        if v == 0:
            raise ValueError("delta must be non-zero")
        return v


# ── Quiz question schemas ─────────────────────────────────────────────────────

class GameQuestionCreate(BaseModel):
    question_text:  str        = Field(..., min_length=1)
    options:        List[str]  = Field(..., min_length=2, max_length=4)
    correct_option: int        = Field(..., ge=0, le=3)
    time_limit:     int        = Field(30, ge=5, le=120)
    points:         int        = Field(1000, ge=100, le=5000)
    order_index:    int        = Field(0, ge=0)

    @field_validator("correct_option")
    @classmethod
    def correct_in_range(cls, v: int, info: Any) -> int:
        opts = info.data.get("options", [])
        if opts and v >= len(opts):
            raise ValueError("correct_option must be a valid index into options")
        return v


class GameQuestionRead(BaseModel):
    id:               int
    session_id:       int
    question_text:    str
    question_text_ru: Optional[str] = None
    options:          List[str]
    correct_option:   Optional[int] = None  # hidden until revealed
    time_limit:     int
    points:         int
    order_index:    int
    status:         QuestionStatus
    activated_at:   Optional[datetime] = None
    created_at:     datetime
    model_config = ConfigDict(from_attributes=True)


class AnswerSubmit(BaseModel):
    chosen_option: int = Field(..., ge=0, le=3)


class AnswerResultRead(BaseModel):
    student_id:    int
    full_name:     Optional[str] = None
    team_id:       int
    chosen_option: int
    is_correct:    bool
    points_earned: int


class QuestionEndPayload(BaseModel):
    question_id:    int
    correct_option: int
    answers:        List[AnswerResultRead]
    team_scores:    List[dict]  # [{team_id, name, color, score}]
