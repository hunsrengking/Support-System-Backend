# app/models/priority.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config.db import Base

class Priority(Base):
    __tablename__ = "priorities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    tickets = relationship("Ticket", back_populates="priority")
