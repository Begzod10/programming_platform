from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.team_game import GameType, SessionStatus


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
    id:          int
    title:       str
    description: Optional[str]     = None
    game_type:   GameType
    status:      SessionStatus
    course_id:   Optional[int]     = None
    course_title: Optional[str]    = None
    created_by:  int
    team_count:  int
    teams:       List[GameTeamRead] = []
    created_at:  datetime
    updated_at:  datetime
    my_team_id:  Optional[int]     = None
    model_config = ConfigDict(from_attributes=True)


class StudentRead(BaseModel):
    id:         int
    full_name:  Optional[str] = None
    username:   Optional[str] = None
    avatar_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class TeamAssignmentItem(BaseModel):
    team_id:     int
    student_ids: List[int]


class StartSessionBody(BaseModel):
    assignments: Optional[List[TeamAssignmentItem]] = None


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
