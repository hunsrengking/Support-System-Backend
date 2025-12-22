from datetime import datetime
from app.services.user_service import getUserById
from app.config.iconfig import FRONTEND_URL


def build_ticket_email_payload(
    db,
    *,
    ticket,
    to_user_id: int,
    action: str,  # ASSIGNED | REASSIGNED | APPROVED | REJECTED
    action_by_id: int,
):
    to_user = getUserById(db, to_user_id)
    action_by = getUserById(db, action_by_id)
    creator = getUserById(db, ticket.created_by_id)

    if not to_user or not to_user.email:
        return None

    message_map = {
        "ASSIGNED": (
            f"You have been assigned a ticket.\n\n"
            f"📌 Title: {ticket.title}\n"
            f"👤 Assigned by: {action_by.username}"
        ),
        "REASSIGNED": (
            f"A ticket has been reassigned to you.\n\n"
            f"📌 Title: {ticket.title}\n"
            f"👤 Assigned by: {action_by.username}"
        ),
        "APPROVED": (
            f"Your ticket has been approved.\n\n"
            f"📌 Title: {ticket.title}\n"
            f"👤 Approved by: {action_by.username}"
        ),
        "REJECTED": (
            f"Your ticket has been rejected.\n\n"
            f"📌 Title: {ticket.title}\n"
            f"👤 Rejected by: {action_by.username}"
        ),
    }

    return {
        "to_email": to_user.email,
        # 📩 CC ticket creator (if different)
        "cc_email": (
            creator.email
            if creator and creator.email and creator.email != to_user.email
            else ""
        ),
        "name": to_user.username,
        "time": datetime.now().strftime("%d %b %Y %H:%M"),
        "message": message_map.get(action),
        "view_url": f"{FRONTEND_URL}/ticket/view/{ticket.id}",
    }
