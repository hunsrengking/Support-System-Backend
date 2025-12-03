from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services import department_service
from app.config.db import get_db
from app.models.user_model import *
from app.middlewares.auth_middlewares import requirepermissions

router = APIRouter()


@router.get("/department")
# @requirepermissions("view_users")
def list_department(db: Session = Depends(get_db)):
    return department_service.getAllDepartment(db)