from sqlalchemy.orm import Session
from app.schema.notification_schema import Notification
from app.models.notification_model import NotificationCreate


def createNotification(db: Session, data: NotificationCreate):
    notification = Notification(**data.dict())
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def getUserNotifications(db: Session, user_id: int, limit: int = 10):
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )


def getUnreadCount(db: Session, user_id: int):
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read == False)
        .count()
    )


def markAsRead(db: Session, notification_id: int, user_id: int):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        .first()
    )

    if notification:
        notification.is_read = True # type: ignore
        db.commit()

    return notification
