from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.config.db import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    image_path = Column(String(255), nullable=True)
    file_path = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)