# app/services/ticket_service.py
from collections import defaultdict
from typing import List, Dict, Any
from sqlalchemy.orm import Session, aliased
from sqlalchemy.exc import SQLAlchemyError
from fastapi import BackgroundTasks, HTTPException, status
from app.schema.ticket_schema import Ticket
from app.schema.item_schema import Item
from app.schema.status_schema import Status
from app.schema.user_schema import User
from app.models.ticket_model import TicketCreateReq, TicketUpdateReq
from app.schema.priority_schema import Priority
from app.schema.category_schema import Category
from app.schema.item_schema import Item
from app.constants.status_constants import *
from app.config.iconfig import FRONTEND_URL
from datetime import datetime
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime
from app.services.user_service import getUserById
from app.services.department_service import getDepartmentById
from app.services.status_service import getPriorityById
from app.middlewares.auth_middlewares import get_current_user
from app.services.telegram_service import (
    getActiveTelegramConfig,
    SendTelegramMessageAsync,
)
from app.services.notification_service import createNotification
from app.models.notification_model import NotificationCreate


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
            Ticket.title.label("subject"),
            Ticket.description.label("description"),
            Ticket.status_id.label("status_id"),
            Status.name.label("status"),
            Ticket.priority_id.label("priority_id"),
            Priority.name.label("priority"),
            Ticket.category_id.label("category_id"),
            Category.name.label("category"),
            Ticket.assigned_to_id.label("assigned_to_id"),
            UserAssigned.username.label("assigned_to"),
            Ticket.requester_id.label("requester_id"),
            UserRequester.username.label("created_by"),
            Ticket.assigned_to_department_id.label("assigned_to_department_id"),
            Ticket.start_date.label("start_date"),
            Ticket.end_date.label("end_date"),
            Ticket.create_date.label("created_at"),
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
    UserRequester = aliased(User)
    UserAssigned = aliased(User)
    rows = (
        db.query(
            Ticket.id,
            Ticket.title,
            UserAssigned.username.label("assigned_to"),
            UserRequester.username.label("created_by"),
            Status.name.label("status"),
            Category.name.label("category"),
            Priority.name.label("priority"),
            Ticket.create_date.label("created_at"),
        )
        .join(UserRequester, Ticket.requester_id == UserRequester.id, isouter=True)
        .join(UserAssigned, Ticket.assigned_to_id == UserAssigned.id, isouter=True)
        .join(Status, Ticket.status_id == Status.id, isouter=True)
        .join(Priority, Ticket.priority_id == Priority.id, isouter=True)
        .join(Category, Ticket.category_id == Category.id, isouter=True)
        .filter(Ticket.status_id == 8)
        .all()
    )
    return [dict(row._mapping) for row in rows]


def createTicket(
    db: Session,
    data: TicketCreateReq,
    user_id: int,
    background_tasks: BackgroundTasks | None = None,
):
    try:
        ticket = Ticket(
            title=data.title,
            description=data.description,
            status_id=STATUS_WAITING_APPROVE,
            requester_id=user_id,
            priority_id=data.priority_id,
            category_id=data.category_id,
            assigned_to_id=data.assigned_to_id,
            assigned_to_department_id=data.assigned_to_department_id,
            start_date=data.start_date,
            end_date=data.end_date,
        )

        db.add(ticket)
        db.flush()

        image_path = None
        file_path = None
        description = None

        if data.items:
            for item in data.items:
                if item.image_path:
                    image_path = item.image_path
                if item.file_path:
                    file_path = item.file_path
                if item.description:
                    description = item.description
            db_item = Item(
                ticket_id=ticket.id,
                image_path=image_path,
                file_path=file_path,
                description=description or "Attachments",
            )
            db.add(db_item)

        db.commit()
        db.refresh(ticket)
        # ================= NOTIFICATION =================
        notify_user_id = (
            ticket.assigned_to_id
            if ticket.assigned_to_id  # type: ignore
            else ticket.requester_id
        )

        createNotification(
            db,
            NotificationCreate(
                user_id=notify_user_id,  # type: ignore
                title="New Ticket Created",
                message=f"Ticket #{ticket.id} - {ticket.title}",
                link=f"/ticket/views/{ticket.id}",
                type="ticket",
            ),
        )

        # ================= TELEGRAM =================
        config = getActiveTelegramConfig(db)
        if config:
            requester = getUserById(db, user_id)
            priority = getPriorityById(db, ticket.priority_id)  # type: ignore
            department = getDepartmentById(db, ticket.assigned_to_department_id)  # type: ignore
            department_name = department["name"] if department else "Not yet assigned"
            priority_name = priority.name if priority else "Not yet assigned"
            deadline = (
                ticket.end_date.strftime("%d %b %Y")
                if ticket.end_date  # type: ignore
                else "Not yet assigned"
            )
            ticket_url = f"{FRONTEND_URL}/ticket/views/{ticket.id}"
            message = (
                f"<b>| New ticket:</b> #{ticket.id}\n"
                f"<b>| Subject:</b> {ticket.title}\n"
                f"<b>| Customer Name:</b> {requester.username}\n\n"  # type: ignore
                f"📣 <b>Hello team,</b> we have created a new ticket and assigned it to the "
                f"<b>{department_name}</b> department. Please check and respond.\n"
                "==============================\n"
                f"🟠 <b>Priority:</b> {priority_name}\n"
                f"⏱ <b>Dateline:</b> {deadline}\n"
                "==============================\n\n"
                f'🔗 <a href="{ticket_url}">View Ticket</a>'
            )

            background_tasks.add_task(  # type: ignore
                SendTelegramMessageAsync,  # type: ignore
                config.bot_token,  # type: ignore
                config.chat_id,  # type: ignore
                message,
            )
        return ticket

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error while creating ticket: {str(e)}",
        )


def UpdateTicket(
    db: Session,
    ticket_id: int,
    data: TicketUpdateReq,
    user_id: int,
    background_tasks: BackgroundTasks | None = None,
):
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        update_data = data.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(ticket, field, value)

        ticket.assigned_by_id = user_id  # type: ignore # audit

        db.commit()
        db.refresh(ticket)

        # ================= NOTIFICATION =================
        notify_user_id = (
            ticket.assigned_to_id if ticket.assigned_to_id else ticket.requester_id  # type: ignore
        )

        createNotification(
            db,
            NotificationCreate(
                user_id=notify_user_id,  # type: ignore
                title="Ticket Updated",
                message=f"Ticket #{ticket.id} has been updated",
                link=f"/ticket/views/{ticket.id}",
                type="ticket",
            ),
        )

        # ================= TELEGRAM =================
        config = getActiveTelegramConfig(db)
        if config and background_tasks:
            updater = getUserById(db, user_id)
            priority = getPriorityById(db, ticket.priority_id)  # type: ignore
            assigned_user = getUserById(db, ticket.assigned_to_id) if ticket.assigned_to_id else None  # type: ignore
            assigned_username = (
                assigned_user.username if assigned_user else "Not assigned"
            )
            priority_name = priority.name if priority else "Not assigned"
            deadline = (
                ticket.end_date.strftime("%d %b %Y")
                if ticket.end_date  # type: ignore
                else "Not assigned"
            )

            ticket_url = f"{FRONTEND_URL}/ticket/views/{ticket.id}"

            message = (
                f"<b>✏️ Ticket Updated</b>  #{ticket.id}\n"
                f"<b>📌 Subject:</b> {ticket.title}\n"
                f"<b>👤 Updated by:</b> {updater.username}\n\n"  # type: ignore
                "📣 <b>Hello team,</b>\n"
                "The following ticket has been updated. Please review the latest details below:\n"
                "==============================\n"
                f"🟠 <b>Priority:</b> {priority_name}\n"
                f"👤 <b>Assigned To:</b> {assigned_username}\n"
                f"⏱ <b>Deadline:</b> {deadline}\n"
                "==============================\n\n"
                f'🔗 <a href="{ticket_url}">View Ticket</a>'
            )

            background_tasks.add_task(
                SendTelegramMessageAsync,
                config.bot_token,  # type: ignore
                config.chat_id,  # type: ignore
                message,
            )

        return ticket

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error while updating ticket: {str(e)}",
        )


def ApproveTicket(id: int, db: Session, user_id: int):
    ticket = db.query(Ticket).filter(Ticket.id == id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.status_id != STATUS_WAITING_APPROVE:  # type: ignore
        raise HTTPException(status_code=400, detail="Ticket not waiting approval")

    ticket.status_id = STATUS_OPEN  # type: ignore
    ticket.approved_by_id = user_id  # type: ignore
    ticket.approved_date = datetime.now()  # type: ignore

    db.commit()
    db.refresh(ticket)

    return {"message": "Ticket approved successfully", "ticket_id": id}


def RejectTicket(id: int, db: Session, user_id: int):
    ticket = db.query(Ticket).filter(Ticket.id == id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.status_id != STATUS_WAITING_APPROVE:  # type: ignore
        raise HTTPException(status_code=400, detail="Ticket not waiting approval")

    ticket.status_id = STATUS_REJECT  # type: ignore
    ticket.approved_by_id = user_id  # type: ignore
    ticket.approved_date = datetime.now()  # type: ignore

    db.commit()
    db.refresh(ticket)
    return {"message": "Ticket reject successfully", "ticket_id": id}


def DeleteTicket(id: int, db: Session, user_id: int):
    ticket = db.query(Ticket).filter(Ticket.id == id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.status_id != STATUS_WAITING_APPROVE:  # type: ignore
        raise HTTPException(status_code=400, detail="Ticket not waiting approval")

    ticket.status_id = STATUS_DELETE  # type: ignore
    ticket.approved_by_id = user_id  # type: ignore
    ticket.approved_date = datetime.now()  # type: ignore

    db.commit()
    db.refresh(ticket)
    return {"message": "Ticket delete successfully", "ticket_id": id}
