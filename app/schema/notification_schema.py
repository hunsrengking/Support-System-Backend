from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.config.db import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(255))
    type = Column(String(50), default="ticket")

    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
