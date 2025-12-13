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
        raise HTTPException(status_code=404, detail=f"Department with id={id} not found")
    return {"message": f"Department with id={id} has been disable"}
