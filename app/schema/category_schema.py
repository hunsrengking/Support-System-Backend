# app/models/category.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config.db import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)

    tickets = relationship("Ticket", back_populates="category")
