from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    link: Optional[str] = None
    type: Optional[str] = "ticket"


class NotificationResp(BaseModel):
    id: int
    title: str
    message: str
    link: Optional[str]
    type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
