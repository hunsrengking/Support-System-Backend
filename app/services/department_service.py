from app.schema.departments_schema import Department
from typing import Optional
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


def getAllDepartment(db):
    return db.query(Department).all()


def getDepartmentById(db, department_id: int):
    return db.query(Department).filter(Department.id == department_id).first()


def createDepartment(db, name: str):
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Department name required")

    existing = db.query(Department).filter(Department.username == name).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Department with this name already exists"
        )

    department = Department(username=name)
    try:
        db.add(department)
        db.commit()
        db.refresh(department)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not create department")

    return department


def updateDepartment(db, department_id: int, name: Optional[str] = None):
    department = db.query(Department).filter(Department.id == department_id).first()
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
