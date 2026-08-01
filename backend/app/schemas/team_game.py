from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import Optional, List, Any, Literal
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
    auto_mode:           bool              = False
    course_id:           Optional[int]      = None
    course_title:        Optional[str]      = None
    created_by:          int
    team_count:          int
    teams:               List[GameTeamRead]  = []
    created_at:          datetime
    updated_at:          datetime
    my_team_id:          Optional[int]      = None
    current_question_id: Optional[int]      = None
    my_auto_completed:   Optional[bool]      = None
    my_auto_answered:    Optional[int]       = None
    my_auto_total:       Optional[int]       = None
    questions_count:     int                = 0
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
    student_ids:      Optional[List[int]]              = None
    team_assignments: Optional[List[TeamAssignmentItem]] = None


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
    options:        List[str]  = Field(..., min_length=2, max_length=6)
    correct_option: int        = Field(..., ge=0, le=5)
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
    options_ru:       Optional[List[str]] = None
    correct_option:   Optional[int] = None  # hidden until revealed
    time_limit:     int
    points:         int
    order_index:    int
    status:         QuestionStatus
    activated_at:   Optional[datetime] = None
    created_at:     datetime
    question_kind:       str            = 'quiz'
    code_snippet:        Optional[str]  = None
    code_language:       Optional[str]  = None
    bug_line:             Optional[int]  = None
    bug_explanation:      Optional[str]  = None
    bug_explanation_ru:   Optional[str]  = None
    model_config = ConfigDict(from_attributes=True)


class AnswerSubmit(BaseModel):
    chosen_option: int = Field(..., ge=0, le=5)


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
    bug_line:            Optional[int] = None
    bug_explanation:      Optional[str] = None
    bug_explanation_ru:   Optional[str] = None


class AutoQuestionRead(BaseModel):
    id:               int
    question_text:    str
    question_text_ru: Optional[str] = None
    options:          List[str]
    options_ru:       Optional[List[str]] = None
    time_limit:       int
    points:           int
    order_index:      int
    # Presentation-only — the answer (bug_line/bug_explanation*) must NEVER
    # be exposed here: this schema serializes straight from the ORM object
    # via from_attributes, so it's the one place a stray field name would
    # silently leak the answer to the student before they submit.
    question_kind: str            = 'quiz'
    code_snippet:  Optional[str]  = None
    code_language: Optional[str]  = None
    model_config = ConfigDict(from_attributes=True)


class AutoRankingEntry(BaseModel):
    id:    int
    name:  str
    color: str
    score: int


class AutoAnswerResultRead(BaseModel):
    student_id:     int
    chosen_option:  int
    correct_option: int
    is_correct:     bool
    points_earned:  int
    my_team_id:     Optional[int] = None
    rankings:       List[AutoRankingEntry] = []
    bug_line:            Optional[int] = None
    bug_explanation:      Optional[str] = None
    bug_explanation_ru:   Optional[str] = None


# ── Bug-hunt question schemas ─────────────────────────────────────────────────

class BugQuestionCreate(BaseModel):
    """Authoring input for a bug-hunt question. The client never sends
    options/correct_option — the server derives them from bug_line +
    distractor_lines (shuffled) so a teacher can't mismark the answer index,
    and so the candidate line numbers can never drift from the snippet."""
    question_text:      str        = Field(..., min_length=1)
    code_snippet:        str        = Field(..., min_length=1, max_length=4000)
    code_language:       Literal['javascript', 'python', 'html', 'css']
    bug_line:             int        = Field(..., ge=1)
    distractor_lines:     List[int]  = Field(..., min_length=2, max_length=5)
    bug_explanation:      str        = Field(..., min_length=1)
    bug_explanation_ru:   Optional[str] = None
    time_limit:          int        = Field(90, ge=5, le=120)
    points:              int        = Field(1500, ge=100, le=5000)

    @field_validator("distractor_lines")
    @classmethod
    def distractors_unique(cls, v: List[int]) -> List[int]:
        if len(v) != len(set(v)):
            raise ValueError("distractor_lines must not contain duplicates")
        if any(n < 1 for n in v):
            raise ValueError("distractor_lines must be >= 1")
        return v

    @model_validator(mode="after")
    def validate_lines(self):
        lines = self.code_snippet.split("\n")
        line_count = len(lines)
        if self.bug_line > line_count:
            raise ValueError(f"bug_line {self.bug_line} exceeds snippet length ({line_count} lines)")
        if any(n > line_count for n in self.distractor_lines):
            raise ValueError(f"distractor_lines must not exceed snippet length ({line_count} lines)")
        if self.bug_line in self.distractor_lines:
            raise ValueError("bug_line must not also appear in distractor_lines")
        return self
