# app/services/staff_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schema.staff_schema import Staff
from app.schema.position_schema import Position
from app.models.staff_model import StaffCreate, StaffUpdate


def get_all_staff(db: Session):
    return (
        db.query(
            Staff.id,
            Staff.external_id,
            Staff.firstname,
            Staff.lastname,
            Staff.display_name,
            Staff.mobile_no,
            Staff.join_on_date,
            Staff.is_active,
            Staff.position_id,
            Position.title.label("position_title"),
        )
        .outerjoin(Position, Staff.position_id == Position.id)
        .order_by(Staff.id.desc())
        .all()
    )


def get_staff_by_id(staff_id: int, db: Session) -> Staff:
    staff = db.query(Staff).filter(Staff.id == staff_id).first()

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff not found",
        )

    return staff


def create_staff(data: StaffCreate, db: Session):
    display_name = data.display_name or f"{data.firstname or ''} {data.lastname or ''}".strip()

    staff = Staff(
        external_id=data.external_id,
        firstname=data.firstname,
        lastname=data.lastname,
        display_name=display_name,
        mobile_no=data.mobile_no,
        join_on_date=data.join_on_date,
        position_id=data.position_id,
        is_active=data.is_active,
    )

    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


def update_staff(staff_id: int, data: StaffUpdate, db: Session):
    staff = get_staff_by_id(staff_id, db)

    for key, value in data.dict(exclude_unset=True).items():
        setattr(staff, key, value)

    if data.firstname is not None or data.lastname is not None:
        staff.display_name = f"{staff.firstname or ''} {staff.lastname or ''}".strip() # type: ignore

    db.commit()
    db.refresh(staff)
    return staff


def delete_staff(staff_id: int, db: Session):
    staff = get_staff_by_id(staff_id, db)
    db.delete(staff)
    db.commit()
    return {"message": "Staff deleted successfully"}
