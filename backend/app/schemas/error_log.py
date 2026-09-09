from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ErrorLogEntry(BaseModel):
    id: int
    method: str
    path: str
    error_type: str
    message: str
    traceback: str
    actor_id: Optional[int]
    actor_username: Optional[str]
    actor_role: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ErrorLogOut(BaseModel):
    items: List[ErrorLogEntry]
