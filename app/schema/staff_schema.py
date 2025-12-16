from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.db import Base


class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), nullable=True)
    firstname = Column(String(255), nullable=True)
    lastname = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=True)
    mobile_no = Column(String(255), nullable=True)
    join_on_date = Column(Date, nullable=True)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # relationship
    position = relationship("Position", back_populates="staff")
    users = relationship("User", back_populates="staff")
