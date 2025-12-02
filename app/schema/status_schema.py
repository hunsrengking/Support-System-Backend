from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.config.db import Base

class Status(Base):
    __tablename__ = "status"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    # Relationships
    departments = relationship("Department", back_populates="status")
    tickets = relationship("Ticket", back_populates="status", cascade="all, delete-orphan")