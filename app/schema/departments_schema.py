from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.config.db import Base
from datetime import datetime

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    status_id = Column(Integer, ForeignKey("status.id"))
    description = Column(String(255), nullable=True)
    create_date = Column(DateTime, nullable=False,default=datetime.utcnow)

    # Reverse relationship
    users = relationship("User", back_populates="department")
    status = relationship("Status", back_populates="departments")
    tickets = relationship("Ticket", back_populates="assigned_to_department")