# app/controllers/staff_controller.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.models.staff_model import (
    StaffCreate,
    StaffUpdate,
    StaffResponse,
)
from app.services import staff_service
from typing import List

router = APIRouter(tags=["Staff"])


@router.get("/staff", response_model=list[StaffResponse])
def get_all_staff(db: Session = Depends(get_db)):
    return staff_service.get_all_staff(db)


@router.get("/staff/{staff_id}")
def get_staff(staff_id: int, db: Session = Depends(get_db)):
    return staff_service.get_staff_by_id(staff_id, db)


@router.post("/staff", response_model=StaffResponse)
def create_staff(data: StaffCreate, db: Session = Depends(get_db)):
    return staff_service.create_staff(data, db)


@router.put("/staff/{staff_id}", response_model=StaffResponse)
def update_staff(
    staff_id: int,
    data: StaffUpdate,
    db: Session = Depends(get_db),
):
    return staff_service.update_staff(staff_id, data, db)


@router.delete("/staff/{staff_id}")
def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    return staff_service.delete_staff(staff_id, db)
