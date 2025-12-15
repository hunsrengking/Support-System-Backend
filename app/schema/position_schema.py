from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.db import Base


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, unique=True)
    level = Column(String(50), nullable=True)
    min_salary = Column(DECIMAL(10, 2), nullable=True)
    max_salary = Column(DECIMAL(10, 2), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # relationship
    staff = relationship("Staff", back_populates="position")
