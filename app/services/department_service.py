from app.schema.departments_schema import Department
from typing import Optional
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


def getAllDepartment(db):
    return db.query(Department).all()


def getDepartmentById(db, department_id: int):
    return db.query(Department).filter(Department.id == department_id).first()


def createDepartment(db, name: str, status_id: int, description: str):
    new_department = Department(
        name=name,
        status_id=status_id,
        description=description,
    )
    try:
        db.add(new_department)
        db.commit()
        db.refresh(new_department)
        return new_department
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Department with this name already exists."
        )


def updateDepartment(
    db,
    department_id: int,
    name: str,
    status_id: int,
    description: str,
):
    department = getDepartmentById(db, department_id)
    if not department:
        raise HTTPException(
            status_code=404, detail=f"Department with id={department_id} not found"
        )

    department.name = name
    department.status_id = status_id
    department.description = description

    try:
        db.commit()
        db.refresh(department)
        return department
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Department with this name already exists."
        )