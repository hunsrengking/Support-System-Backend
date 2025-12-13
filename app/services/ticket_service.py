# app/services/ticket_service.py
from collections import defaultdict
from typing import List, Dict, Any
from sqlalchemy.orm import Session, aliased
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from app.schema.ticket_schema import Ticket
from app.schema.item_schema import Item
from app.schema.status_schema import Status
from app.schema.user_schema import User
from app.models.ticket_model import TicketCreateReq
from app.schema.priority_schema import Priority
from app.schema.category_schema import Category
from app.schema.item_schema import Item
from app.constants.status_constants import *
from datetime import datetime
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime


def getAllTicket(db: Session) -> List[Dict[str, Any]]:
    rows = (
        db.query(
            Ticket.id.label("id"),
            Ticket.title.label("title"),
            Status.name.label("status"),
            Priority.name.label("priority"),
            Category.name.label("category"),
            Ticket.create_date.label("create_date"),
            Ticket.start_date.label("start_date"),
            Ticket.end_date.label("end_date"),
            User.username.label("assigned_to"),
        )
        .join(User, Ticket.assigned_to_id == User.id, isouter=True)
        .join(Status, Ticket.status_id == Status.id, isouter=True)
        .join(Priority, Ticket.priority_id == Priority.id, isouter=True)
        .join(Category, Ticket.category_id == Category.id, isouter=True)
        .filter(Ticket.status_id.in_([3, 4, 5, 6, 7]))
        .all()
    )

    tickets = [dict(r._mapping) for r in rows]
    if not tickets:
        return []

    ticket_ids = [t["id"] for t in tickets]

    # 2) load all items for these tickets
    item_rows = (
        db.query(
            Item.ticket_id.label("ticket_id"),
            Item.image_path.label("image_path"),
            Item.file_path.label("file_path"),
            Item.description.label("description"),
            Item.id.label("id"),
        )
        .filter(Item.ticket_id.in_(ticket_ids))
        .all()
    )

    items_by_ticket = defaultdict(list)
    for r in item_rows:
        item = dict(r._mapping)
        tid = item.pop("ticket_id")
        items_by_ticket[tid].append(item)
    for t in tickets:
        t["items"] = items_by_ticket.get(t["id"], [])
    return tickets


def getTicketById(db: Session, ticket_id: int):
    UserRequester = aliased(User)
    UserAssigned = aliased(User)
    row = (
        db.query(
            Ticket.id.label("id"),
            Ticket.title.label("title"),
            Ticket.description.label("description"),
            Ticket.status_id.label("status_id"),
            Status.name.label("status_name"),
            Ticket.priority_id.label("priority_id"),
            Priority.name.label("priority_name"),
            Ticket.category_id.label("category_id"),
            Category.name.label("category_name"),
            Ticket.assigned_to_id.label("assigned_to_id"),
            UserAssigned.username.label("assigned_to"),
            Ticket.requester_id.label("requester_id"),
            UserRequester.username.label("created_by"),
            Ticket.assigned_to_department_id.label("assigned_to_department_id"),
            Ticket.start_date.label("start_date"),
            Ticket.end_date.label("end_date"),
            Ticket.create_date.label("create_date"),
            Ticket.approved_date.label("approved_date"),
            Ticket.approved_by_id.label("approved_by_id"),
        )
        .join(UserRequester, Ticket.requester_id == UserRequester.id, isouter=True)
        .join(UserAssigned, Ticket.assigned_to_id == UserAssigned.id, isouter=True)
        .join(Status, Ticket.status_id == Status.id, isouter=True)
        .join(Priority, Ticket.priority_id == Priority.id, isouter=True)
        .join(Category, Ticket.category_id == Category.id, isouter=True)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id={ticket_id} not found",
        )

    # Convert ticket main data
    ticket = dict(row._mapping)

    # 2) Load related items (1-to-many)
    item_rows = (
        db.query(
            Item.id.label("id"),
            Item.image_path.label("image_path"),
            Item.file_path.label("file_path"),
            Item.description.label("description"),
        )
        .filter(Item.ticket_id == ticket_id)
        .all()
    )

    ticket["items"] = [dict(r._mapping) for r in item_rows]

    return ticket


def getTicketByStautus(db: Session):
    rows = db.query(Ticket.id, Ticket.title).filter(Ticket.status_id == 8).all()
    return [dict(row._mapping) for row in rows]


def createTicket(db: Session, data: TicketCreateReq) -> Ticket:
    try:
        ticket = Ticket(
            title=data.title,
            description=data.description,
            status_id=STATUS_WAITING_APPROVE,
            requester_id=data.requester_id,
            assigned_by_id=data.assigned_by_id,
            priority_id=data.priority_id,
            category_id=data.category_id,
            assigned_to_id=data.assigned_to_id,
            assigned_to_department_id=data.assigned_to_department_id,
            start_date=data.start_date,
            end_date=data.end_date,
        )

        db.add(ticket)
        db.flush()

        if data.items:
            for item in data.items:
                db_item = Item(
                    ticket_id=ticket.id,
                    image_path=item.image_path,
                    file_path=item.file_path,
                    description=item.description,
                )
                db.add(db_item)

        db.commit()
        db.refresh(ticket)
        return ticket

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error while creating ticket: {str(e)}",
        )

def ApproveTicket(id: int, db: Session, user_id: int):
    ticket = db.query(Ticket).filter(Ticket.id == id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.status_id != STATUS_WAITING_APPROVE: # type: ignore
        raise HTTPException(status_code=400, detail="Ticket not waiting approval")

    ticket.status_id = STATUS_OPEN # type: ignore
    ticket.approved_by_id = user_id # type: ignore
    ticket.approved_date = datetime.now() # type: ignore

    db.commit()
    db.refresh(ticket)

    return {"message": "Ticket approved successfully", "ticket_id": id}