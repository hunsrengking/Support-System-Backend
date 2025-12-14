# app/models/ticket.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.config.db import Base
from datetime import datetime


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(String(500), nullable=True)
    status_id = Column(Integer, ForeignKey("status.id"), nullable=False, default=10)
    priority_id = Column(Integer, ForeignKey("priorities.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to_department_id = Column(
        Integer, ForeignKey("departments.id"), nullable=True
    )
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    create_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    approved_date = Column(DateTime, nullable=True)

    # Relationships
    category = relationship("Category", back_populates="tickets")
    priority = relationship("Priority", back_populates="tickets")
    status = relationship("Status", back_populates="tickets")

    assigned_to = relationship(
        "User", foreign_keys=[assigned_to_id], back_populates="tickets_assigned"
    )
    requester = relationship(
        "User", foreign_keys=[requester_id], back_populates="tickets_requested"
    )
    approved_by = relationship(
        "User", foreign_keys=[approved_by_id], back_populates="tickets_approved"
    )
    assigned_to_department = relationship("Department", back_populates="tickets")
