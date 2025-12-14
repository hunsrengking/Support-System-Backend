from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.middlewares.auth_middlewares import get_current_user
from app.schema.user_schema import User
from app.models.notification_model import NotificationResp
from app.services.notification_service import (
    getUserNotifications,
    getUnreadCount,
    markAsRead,
)

router = APIRouter(tags=["Notifications"])


@router.get("/notifications", response_model=list[NotificationResp])
def listNotifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return getUserNotifications(db, current_user.id) # type: ignore


@router.get("/notifications/unread-count")
def unreadCount(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {"count": getUnreadCount(db, current_user.id)} # type: ignore


@router.put("/notifications/{notification_id}/read")
def readNotification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    markAsRead(db, notification_id, current_user.id) # type: ignore
    return {"message": "Notification marked as read"}
