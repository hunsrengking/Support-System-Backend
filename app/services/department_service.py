from app.schema.user_schema import User
from typing import Optional
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


def getAllDepartment(db):
    return db.query(User).all()


def getDepartmentById(db, department_id: int):
    return db.query(User).filter(User.id == department_id).first()


def createDepartment(db, name: str):
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Department name required")

    existing = db.query(User).filter(User.username == name).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Department with this name already exists"
        )

    department = User(username=name)
    try:
        db.add(department)
        db.commit()
        db.refresh(department)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not create department")

    return department


def updateDepartment(db, department_id: int, name: Optional[str] = None):
    department = db.query(User).filter(User.id == department_id).first()
    if not department:
        return None
    if name:
        department.username = name
    try:
        db.add(department)
        db.commit()
        db.refresh(department)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return department
