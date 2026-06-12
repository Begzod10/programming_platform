"""Schemas for the public student profile page (/u/<username>).

Deliberately separate from UserRead — public profiles must never leak
email, phone, balance, gennis_token, or any other private field. Adding
new public fields means adding them here explicitly, so a future change
to UserRead can't accidentally widen the public surface.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class PublicAchievement(BaseModel):
    """One earned badge on the public profile."""
    name: str
    description: Optional[str] = None
    badge_image_url: Optional[str] = None
    points_reward: int = 0
    earned_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublicCertificate(BaseModel):
    """One course certificate, surfaced as a credential on the profile."""
    course_title: str
    issued_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublicProfile(BaseModel):
    """Sanitized shape rendered at /u/<username>.

    Any field added here becomes visible to the entire internet (including
    crawlers and OG-tag scrapers), so add deliberately.
    """
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    current_level: Optional[str] = "Beginner"
    total_points: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    joined_at: datetime

    projects_approved: int = 0
    certificates: List[PublicCertificate] = []
    achievements: List[PublicAchievement] = []

    model_config = ConfigDict(from_attributes=True)
