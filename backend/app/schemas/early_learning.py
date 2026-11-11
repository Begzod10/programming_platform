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
    earned_stars_today: int = 0
    # Home-page helpers: which section the module is filed under (derived
    # from its games, see services/early_sections.py), how many of its games
    # this student has played at least once, and when they last played one.
    section: str = "world"
    completed_count: int = 0
    last_played_at: Optional[datetime] = None


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
    today_stars: int = 0


class EarlyModuleDetail(EarlyModuleListItem):
    activities: List[EarlyActivityOut]


class EarlyPublicModuleListItem(EarlyModuleListItem):
    """Guest ("no login", /play in the frontend) variant of
    EarlyModuleListItem. earned_stars always comes back 0 here — there's no
    Student to scope an EarlyActivityCompletion to, so the guest frontend
    tracks its own progress in localStorage and needs each visible
    activity's id to sum it per module; the authed list doesn't expose this
    since its earned_stars is already server-computed from real rows."""

    activity_ids: List[int]


class EarlyPublicModuleDetail(EarlyPublicModuleListItem):
    activities: List[EarlyActivityOut]


class EarlyActivityCompleteIn(BaseModel):
    stars: int = Field(ge=0, le=3)


class EarlyStickerOut(BaseModel):
    """A sticker just earned — both names travel together so the play
    screens need not pass their language to the completion call."""
    key: str
    emoji: str
    name: str
    name_ru: str
    kind: str
    rarity: str


class EarlyAlbumStickerOut(BaseModel):
    key: str
    emoji: str
    name: str
    kind: str
    rarity: str
    owned: bool
    is_new: bool
    hint: Optional[str] = None


class EarlyAlbumToday(BaseModel):
    played: int
    needed: int
    earned: bool


class EarlyAlbumNextStar(BaseModel):
    at: int
    have: int


class EarlyAlbumOut(BaseModel):
    owned_count: int
    total: int
    streak: int
    today: EarlyAlbumToday
    next_star: Optional[EarlyAlbumNextStar] = None
    stickers: List[EarlyAlbumStickerOut]


class EarlyStickersSeenOut(BaseModel):
    marked: int


class EarlyActivityCompleteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    activity_id: int
    stars_earned: int
    attempts: int
    first_completed_at: datetime
    new_stickers: List[EarlyStickerOut] = []


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
