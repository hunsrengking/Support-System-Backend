from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.services import ticket_service

router = APIRouter(tags=["tickets"])


def listTicket(db: Session = Depends(get_db)):
    ticket = ticket_service.getAllTicket(db)
    return ticket
