from sqlalchemy import case
from sqlalchemy.orm import joinedload
from app.schema.user_schema import User
from app.schema.role_schema import Role
from app.schema.departments_schema import Department
from app.schema.staff_schema import Staff
from passlib.context import CryptContext
from typing import Optional
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def create_user(
    db,
    username: str,
    email: str,
    password: str,
    role_id: int,
    department_id: int,
    staff_id: int,
):
    try:
        if db.query(User).filter(User.email == email, User.is_delete == 0).first():
            raise HTTPException(status_code=400, detail="Email already exists.")
        elif (
            db.query(User)
            .filter(User.username == username, User.is_delete == 0)
            .first()
        ):
            raise HTTPException(status_code=400, detail="Username already exists.")
        else:
            hashed_password = pwd_context.hash(password)
            new_user = User(
                username=username,
                email=email,
                password=hashed_password,
                role_id=role_id,
                department_id=department_id,
                staff_id=staff_id,
                is_delete=0,
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def update_user(
    db,
    user_id: int,
    username: Optional[str] = None,
    password: Optional[str] = None,
    email: Optional[str] = None,
    role_id: Optional[int] = None,
    department_id: Optional[int] = None,
    staff_id: Optional[int] = None,
):
    user = db.query(User).filter(User.id == user_id, User.is_delete == 0).first()
    if not user:
        return None
    if username:
        user.username = username
    if email:
        user.email = email
    if role_id:
        user.role_id = role_id
    if department_id:
        user.department_id = department_id
    if staff_id:
        user.staff_id = staff_id

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return user


def delete_user(db, user_id: int):
    user = db.query(User).filter(User.id == user_id, User.is_delete == 0).first()
    if not user:
        return None
    user.is_delete = 1
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return user


def admin_change_password(db, user_id: int, new_password: str):
    if not new_password or new_password.strip() == "":
        raise HTTPException(status_code=400, detail="Password cannot be empty.")

    user = db.query(User).filter(User.id == user_id, User.is_delete == 0).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id={user_id} not found")

    try:
        user.password = pwd_context.hash(new_password)
        db.commit()
        db.refresh(user)
        return {"message": "Password changed successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def change_password(db, user_id: int, old_password, new_password: str):
    if not new_password or new_password.strip() == "":
        raise HTTPException(status_code=400, detail="New password cannot be empty.")
    elif not old_password or old_password.strip() == "":
        raise HTTPException(status_code=400, detail="Old password cannot be empty.")
    else:
        user = db.query(User).filter(User.id == user_id, User.is_delete == 0).first()
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User with id={user_id} not found"
            )
        elif not pwd_context.verify(old_password, user.password):
            raise HTTPException(status_code=400, detail="Old password is incorrect.")
        else:
            user.password = pwd_context.hash(new_password)
        try:
            db.commit()
            db.refresh(user)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        return user


def getUserByEmail(db, email: str):
    return db.query(User).filter(User.email == email, User.is_delete == 0).first()


# def getUserById(db, id: int):
#     return db.query(User).filter(User.id == id, User.is_delete == 0).first()


def getUserById(db, id: int):
    return (
        db.query(User)
        .options(
            joinedload(User.role).joinedload(Role.permissions),
            joinedload(User.staff),  # ✅ JOIN staff
        )
        .filter(User.id == id, User.is_delete == 0)
        .first()
    )


def getAllUser(db):
    status_case = case(
        (User.is_locked == 1, "Locked"),
        (User.is_delete == 0, "Active"),
        else_="Deleted",
    )

    rows = (
        db.query(
            User.id,
            User.username,
            User.email,
            User.role_id,
            User.department_id,
            User.staff_id,  # ✅ staff_id
            User.is_delete,
            status_case.label("status"),
            Role.name.label("role_name"),
            Department.name.label("department_name"),
            Staff.display_name.label("staff_name"),  # ✅ staff
        )
        .join(Role, User.role_id == Role.id, isouter=True)
        .join(Department, User.department_id == Department.id, isouter=True)
        .join(Staff, User.staff_id == Staff.id, isouter=True)  # ✅ JOIN staff
        .filter(User.is_delete == 0)
        .all()
    )

    # ✅ Convert tuple → dict (IMPORTANT)
    return [dict(row._mapping) for row in rows]


def has_permission(user, permission_name: str):
    if not user.role:
        return False
    return any(p.name == permission_name for p in user.role.permissions)
