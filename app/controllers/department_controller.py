from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services import department_service
from app.config.db import get_db
from app.models.user_model import *
from app.models.department_model import DepartmentModel
from app.middlewares.auth_middlewares import requirepermissions

router = APIRouter()


@router.get("/department")
# @requirepermissions("view_department")
def list_department(db: Session = Depends(get_db)):
    return department_service.getAllDepartment(db)


@router.get("/department/{id}")
# @requirepermissions("view_department")
def getDepartmentById(id: int, db: Session = Depends(get_db)):
    department = department_service.getDepartmentById(db, id)
    if not department:
        raise HTTPException(
            status_code=404, detail=f"Department with id={id} not found"
        )
    return department


@router.post("/department")
# @requirepermissions("create_department")
def createDepartment(data: DepartmentModel, db: Session = Depends(get_db)):
    return (
        department_service.createDepartment(
            db,
            data.name,
            data.status_id,
            data.description,
        ),
    )


@router.delete("/department/{id}")
# @requirepermissions("delete_department")
def DisableDepartment(id: int, db: Session = Depends(get_db)):
    DisableDepartment = department_service.DisableDepartment(db, id)
    if not DisableDepartment:
        raise HTTPException(
            status_code=404, detail=f"Department with id={id} not found"
        )
    return {"message": f"Department with id={id} has been disable"}


# ===============================
# ADD MEMBER TO DEPARTMENT
# ===============================
@router.post("/department/{id}/members/add")
def add_department_member(id: int, payload: dict, db: Session = Depends(get_db)):
    user_id = payload.get("userId")
    if not user_id:
        raise HTTPException(status_code=400, detail="userId is required")

    return department_service.addMemberToDepartment(db, id, user_id)


# ===============================
# REMOVE MEMBER FROM DEPARTMENT
# ===============================
@router.delete("/department/{id}/members/{user_id}remove")
def remove_department_member(id: int, user_id: int, db: Session = Depends(get_db)):
    return department_service.removeMemberFromDepartment(db, id, user_id)
