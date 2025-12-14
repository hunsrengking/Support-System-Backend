from sqlalchemy import Column, Integer, String
from app.config.db import Base

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    group = Column(String(50), nullable=False)