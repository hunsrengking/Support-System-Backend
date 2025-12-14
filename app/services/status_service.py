from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schema.status_schema import Status
from app.schema.category_schema import Category
from app.schema.priority_schema import Priority


def getAllStatus(db: Session) -> List[Status]:
    return db.query(Status).filter(Status.id.in_([3, 4, 5, 6, 7])).all()


def getAllCategory(db: Session) -> List[Category]:
    return db.query(Category).all()


def getAllPriority(db: Session) -> List[Priority]:
    return db.query(Priority).all()


def getPriorityById(db: Session, priority_id: int):
    return db.query(Priority).filter(Priority.id == priority_id).first()
