from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    id: int
    type: str
    tone: str
    title: str
    body: Optional[str] = None
    extra: Optional[str] = None
    points: int
    link: Optional[str] = None
    icon: Optional[str] = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationList(BaseModel):
    items: List[NotificationRead]
    unread_count: int


class UnreadCount(BaseModel):
    unread_count: int
