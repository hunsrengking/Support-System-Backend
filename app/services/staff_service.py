# app/services/staff_service.py
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.staff_model import StaffCreate, StaffUpdate
from app.schema.staff_schema import Staff
from app.schema.position_schema import Position


def get_all_staff(db: Session):
    rows = (
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


def get_staff_by_id(staff_id: int, db: Session):
    r = (
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
        .filter(Staff.id == staff_id)
        .first()  # ✅ IMPORTANT
    )

    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff not found",
        )

    return {
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


def create_staff(data: StaffCreate, db: Session):
    try:
        # auto-generate display_name if missing
        display_name = data.display_name
        if not display_name:
            display_name = f"{data.firstname or ''} {data.lastname or ''}".strip()

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

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


def update_staff(staff_id: int, data: StaffUpdate, db: Session):
    staff = get_staff_by_id(staff_id, db)

    try:
        for key, value in data.dict(exclude_unset=True).items():
            setattr(staff, key, value)

        # regenerate display_name if firstname/lastname updated
        if data.firstname is not None or data.lastname is not None:
            staff.display_name = (  # type: ignore
                f"{staff.firstname or ''} {staff.lastname or ''}".strip()  # type: ignore
            )

        db.commit()
        db.refresh(staff)
        return staff

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


def delete_staff(staff_id: int, db: Session):
    staff = get_staff_by_id(staff_id, db)

    try:
        db.delete(staff)
        db.commit()
        return {"message": "Staff deleted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
