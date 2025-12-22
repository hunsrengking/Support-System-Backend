from app.schema.departments_schema import Department
from app.schema.user_schema import User
from typing import Optional, List
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy.orm import joinedload


def getAllDepartment(db):
    return db.query(Department).filter(Department.status_id == 1).all()


def getDepartmentById(db, department_id: int):
    rows = (
        db.query(
            Department.id.label("department_id"),
            Department.name.label("department_name"),
            Department.status_id.label("status_id"),
            User.id.label("user_id"),
            User.username.label("username"),
            User.email.label("email"),
        )
        .outerjoin(User, User.department_id == Department.id)
        .filter(Department.id == department_id)
        .all()
    )

    if not rows:
        return None

    department = {
        "id": rows[0].department_id,
        "name": rows[0].department_name,
        "status_id": rows[0].status_id,
        "members": [],
    }

    for r in rows:
        if r.user_id:
            department["members"].append(
                {
                    "id": r.user_id,
                    "username": r.username,
                    "email": r.email,
                }
            )

    return department


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


from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import exists


def DisableDepartment(db: Session, department_id: int):
    # Get active department
    department = (
        db.query(Department)
        .filter(Department.id == department_id, Department.status_id == 1)
        .first()
    )

    if not department:
        raise HTTPException(
            status_code=404, detail="Department not found or already disabled"
        )

    # Check if department has active users
    has_active_users = db.query(
        exists().where(User.department_id == department_id, User.is_delete == 0)
    ).scalar()

    if has_active_users:
        raise HTTPException(
            status_code=400, detail="Cannot disable department with active users"
        )

    # Disable department
    department.status_id = 2  # type: ignore

    try:
        db.commit()
        db.refresh(department)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return department


def addMemberToDepartment(db: Session, department_id: int, user_id: int):
    department = (
        db.query(Department)
        .filter(Department.id == department_id, Department.status_id == 1)
        .first()
    )

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    user = db.query(User).filter(User.id == user_id, User.is_delete == 0).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.department_id == department_id: # type: ignore
        raise HTTPException(status_code=400, detail="User already in this department")

    user.department_id = department_id # type: ignore

    try:
        db.commit()
        db.refresh(user)
        return {"message": "Member added successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ==================================
# REMOVE MEMBER
# ==================================
def removeMemberFromDepartment(db: Session, department_id: int, user_id: int):
    user = (
        db.query(User)
        .filter(
            User.id == user_id, User.department_id == department_id, User.is_delete == 0
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found in this department")

    user.department_id = None # type: ignore

    try:
        db.commit()
        db.refresh(user)
        return {"message": "Member removed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
