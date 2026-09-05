"""Schemas for the early-learning (age 5-8) module/activity feature.

Read-only content + one write action (submit a completion). No admin/author
schemas yet — content ships via backend/scripts/_seed_early_learning.py, per
the current dev-seeded-content decision (see early_learning.py model docs).
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.early_learning import EarlySubject, EarlyActivityType


class EarlyModuleListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    subject: EarlySubject
    icon_emoji: Optional[str] = None
    color_accent: Optional[str] = None
    display_order: int
    activities_count: int
    earned_stars: int
    max_stars: int


class EarlyActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    order: int
    activity_type: EarlyActivityType
    instruction_text: Optional[str] = None
    content: Dict[str, Any]
    max_stars: int
    best_stars: int
    attempts: int


class EarlyModuleDetail(EarlyModuleListItem):
    activities: List[EarlyActivityOut]


class EarlyActivityCompleteIn(BaseModel):
    stars: int = Field(ge=0, le=3)


class EarlyActivityCompleteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    activity_id: int
    stars_earned: int
    attempts: int
    first_completed_at: datetime


class EarlyLeaderboardEntry(BaseModel):
    student_id: int
    name: str
    avatar_url: Optional[str] = None
    total_stars: int
    rank: int
    is_me: bool


class EarlyLeaderboardOut(BaseModel):
    has_class: bool
    entries: List[EarlyLeaderboardEntry]
