from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schema.ticket_schema import Ticket


def getAllTicket(db: Session) -> List[Ticket]:
    return db.query(Ticket).all()


def getTicketById(db: Session, ticket_id: int) -> Ticket | None:
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def createTicket(db: Session, title: str, description: str | None = None) -> Ticket:
    title = title.strip()
    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket title required"
        )

    ticket = Ticket(title=title, description=description)
    try:
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create ticket",
        )

    return ticket
