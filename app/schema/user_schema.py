from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.config.db import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    is_delete = Column(Integer, default=0)
    username = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_locked = Column(Integer, nullable=False, default=0)
    create_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    failed_attempts = Column(Integer, default=0)

    # Relationships
    role = relationship("Role")
    department = relationship("Department", back_populates="users")
    staff = relationship("Staff", back_populates="users")
    tickets_assigned = relationship(
        "Ticket", back_populates="assigned_to", foreign_keys="[Ticket.assigned_to_id]"
    )
    tickets_requested = relationship(
        "Ticket", back_populates="requester", foreign_keys="[Ticket.requester_id]"
    )
    tickets_approved = relationship(
        "Ticket", back_populates="approved_by", foreign_keys="[Ticket.approved_by_id]"
    )
