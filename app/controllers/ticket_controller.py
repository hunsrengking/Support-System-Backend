# app/controllers/ticket_controller.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.services import ticket_service
from app.models.ticket_model import (
    TicketCreateReq,
    TicketResp,
    ApproveReq,
)
from app.middlewares.auth_middlewares import get_current_user
from app.schema.user_schema import User

router = APIRouter(tags=["tickets"])


@router.get("/ticket")
def ListAllTicket(db: Session = Depends(get_db)):
    return ticket_service.getAllTicket(db)


@router.get("/ticket/{id}")
def getTicketById(id: int, db: Session = Depends(get_db)):
    ticket = ticket_service.getTicketById(db, id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id={id} not found",
        )
    return ticket


@router.get("/ticket/status/waitingapprove")
def getTicketByStatus(db: Session = Depends(get_db)):
    return ticket_service.getTicketByStautus(db)


@router.post(
    "/ticket",
    response_model=TicketResp,
)
def CreateTicket(data: TicketCreateReq, db: Session = Depends(get_db)):
    return ticket_service.createTicket(db, data)


@router.patch("/ticket/{id}/approve")
def ApproveTicket(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ticket_service.ApproveTicket(id=id, db=db, user_id=current_user.id) # type: ignore
