from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class PositionBase(BaseModel):
    title: str
    level: Optional[str] = None
    min_salary: Optional[Decimal] = None
    max_salary: Optional[Decimal] = None
    is_active: Optional[bool] = True


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    title: Optional[str] = None
    level: Optional[str] = None
    min_salary: Optional[Decimal] = None
    max_salary: Optional[Decimal] = None
    is_active: Optional[bool] = None


class PositionResponse(PositionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy → Pydantic
