from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.services import user_service
from app.config.db import get_db
from app.models.user_model import *
from app.middlewares.auth_middlewares import requirepermissions

router = APIRouter()


@router.get("/users")
# @requirepermissions("view_users")
def list_users(db: Session = Depends(get_db)):
    return user_service.getAllUser(db)


@router.get("/users/{id}")
# @requirepermissions("view_users")
def getUserById(id: int, db: Session = Depends(get_db)):
    user = user_service.getUserById(db, id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id={id} not found")
    return user


@router.post("/users")
# @requirepermissions("create_users")
def createUser(data: UserModel, db: Session = Depends(get_db)):
    return (
        user_service.create_user(
            db,
            data.username,
            data.email,
            data.password,
            data.role_id,
            data.department_id,
            data.staff_id,
        ),
    )


@router.put("/users/{user_id}")
# @requirepermissions("edit_users")
def updateUser(
    user_id: int,
    data: UserModel,
    db: Session = Depends(get_db),
):
    updated_user = user_service.update_user(
        db,
        user_id,
        username=data.username,
        email=data.email,
        password=data.password,
        role_id=data.role_id,
        department_id=data.department_id,
        staff_id=data.staff_id,
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail=f"User with id={user_id} not found")
    return updated_user


@router.delete("/users/{user_id}")
# @requirepermissions("delete_users")
def deleteUser(user_id: int, db: Session = Depends(get_db)):
    deleted_user = user_service.delete_user(db, user_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail=f"User with id={user_id} not found")
    return {"message": f"User with id={user_id} has been deleted"}


@router.patch("/users/{user_id}/change-password")
# @requirepermissions("change_user_password")
def adminChangeUserPassword(
    user_id: int,
    data: dict,
    db: Session = Depends(get_db),
):
    password = data.get("password")
    return user_service.admin_change_password(db, user_id, password)  # type: ignore


@router.post("/users/{user_id}/changepassword")
def changeUserPassword(
    user_id: int,
    data: ChangePasswordModel,
    db: Session = Depends(get_db),
):
    return user_service.change_password(
        db,
        user_id,
        data.old_password,
        data.new_password,
    )


@router.get("/users/without/departmemt")
def get_users_without_department(db: Session = Depends(get_db)):
    return user_service.getUsersWithoutDepartment(db)
