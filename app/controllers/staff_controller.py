# app/controllers/staff_controller.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.config.db import get_db
from app.models.staff_model import (
    StaffCreate,
    StaffUpdate,
    StaffResponse,
)
from app.services import staff_service

router = APIRouter(tags=["Staff"])


@router.get("/staff", response_model=List[StaffResponse])
def get_all_staff(db: Session = Depends(get_db)):
    rows = staff_service.get_all_staff(db)

    return [
        {
            "id": r.id,
            "external_id": r.external_id,
            "firstname": r.firstname,
            "lastname": r.lastname,
            "display_name": r.display_name,
            "mobile_no": r.mobile_no,
            "join_on_date": r.join_on_date,
            "is_active": r.is_active,
            "position_id": r.position_id,
            "position_title": r.position_title,
        }
        for r in rows
    ]


@router.get("/staff/{staff_id}", response_model=StaffResponse)
def get_staff(staff_id: int, db: Session = Depends(get_db)):
    staff = staff_service.get_staff_by_id(staff_id, db)

    return {
        "id": staff.id,
        "external_id": staff.external_id,
        "firstname": staff.firstname,
        "lastname": staff.lastname,
        "display_name": staff.display_name,
        "mobile_no": staff.mobile_no,
        "join_on_date": staff.join_on_date,
        "is_active": staff.is_active,
        "position_id": staff.position_id,
        "position_title": staff.position.title if staff.position else None,
    }


@router.post("/staff", response_model=StaffResponse)
def create_staff(data: StaffCreate, db: Session = Depends(get_db)):
    staff = staff_service.create_staff(data, db)

    return {
        "id": staff.id,
        "external_id": staff.external_id,
        "firstname": staff.firstname,
        "lastname": staff.lastname,
        "display_name": staff.display_name,
        "mobile_no": staff.mobile_no,
        "join_on_date": staff.join_on_date,
        "is_active": staff.is_active,
        "position_id": staff.position_id,
        "position_title": staff.position.title if staff.position else None,
    }


@router.put("/staff/{staff_id}", response_model=StaffResponse)
def update_staff(
    staff_id: int,
    data: StaffUpdate,
    db: Session = Depends(get_db),
):
    staff = staff_service.update_staff(staff_id, data, db)

    return {
        "id": staff.id,
        "external_id": staff.external_id,
        "firstname": staff.firstname,
        "lastname": staff.lastname,
        "display_name": staff.display_name,
        "mobile_no": staff.mobile_no,
        "join_on_date": staff.join_on_date,
        "is_active": staff.is_active,
        "position_id": staff.position_id,
        "position_title": staff.position.title if staff.position else None,
    }


@router.delete("/staff/{staff_id}")
def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    return staff_service.delete_staff(staff_id, db)
