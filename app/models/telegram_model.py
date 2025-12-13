from pydantic import BaseModel
from typing import Optional


class TelegramConfigBase(BaseModel):
    bot_token: str
    chat_id: str
    is_active: Optional[bool] = True


class TelegramConfigCreate(TelegramConfigBase):
    pass


class TelegramConfigUpdate(BaseModel):
    bot_token: Optional[str]
    chat_id: Optional[str]
    is_active: Optional[bool]


class TelegramConfigResponse(TelegramConfigBase):
    id: int

    class Config:
        from_attributes = True
