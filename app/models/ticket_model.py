from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ----------------------------
# Item Schemas
# ----------------------------
class ItemCreateReq(BaseModel):
    image_path: Optional[str] = None
    file_path: Optional[str] = None
    description: Optional[str] = None


class ItemResp(BaseModel):
    id: int
    image_path: Optional[str] = None
    file_path: Optional[str] = None
    description: Optional[str] = None


# ----------------------------
# Ticket Create & Update
# ----------------------------
class TicketCreateReq(BaseModel):
    title: str
    description: Optional[str] = None
    priority_id: Optional[int] = None
    category_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    assigned_to_department_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    items: Optional[List[ItemCreateReq]] = None


class TicketUpdateReq(BaseModel):
    description: Optional[str] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    category_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    assigned_to_department_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# ----------------------------
# Ticket Response (matches ticket_model.to_dict())
# ----------------------------
class TicketResp(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status_id: int
    status_name: Optional[str] = None
    priority_id: Optional[int] = None
    priority_name: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    assigned_to_id: Optional[int] = None
    assigned_to_name: Optional[str] = None
    assigned_to_department_id: Optional[int] = None
    assigned_by_id: Optional[int] = None
    approved_by_id: Optional[int] = None

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    create_date: Optional[datetime] = None
    approved_date: Optional[datetime] = None

    items: Optional[List[ItemResp]] = None

    class Config:
        orm_mode = True

class ApproveReq(BaseModel):
        approver_id: Optional[int] = None
        approved_date: Optional[datetime] = None
