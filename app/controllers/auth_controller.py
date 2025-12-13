# app/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.config.db import get_db
from app.services import user_service
from app.services import auth_service  # your existing token service

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # 1) Find user by email
    user = user_service.getUserByEmail(db, payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # 2) Read stored hash
    stored_hash = getattr(user, "password", None)
    if not stored_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    # 3) Verify password
    if not pwd_context.verify(payload.password, stored_hash):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # 4) Collect role + permissions
    role_data = None
    permissions_list = []

    if getattr(user, "role", None):
        role_data = {
            "id": user.role.id,
            "name": getattr(user.role, "name", None),
        }

        if getattr(user.role, "permissions", None):
            permissions_list = [
                {
                    "id": perm.id,
                    "name": getattr(perm, "name", None),
                }
                for perm in user.role.permissions
            ]

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "name": getattr(user, "username", ""),
        "role_id": user.role_id,
        "role": role_data,
        "permissions": permissions_list,
    }

    access_token = auth_service.create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role_id": user.role_id,
            "role": role_data,
            "permissions": permissions_list,
        },
    }


@router.post("/logout")
def logout(request: Request):
    auth_header = request.headers.get("authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing or invalid Authorization header",
        )
    token = auth_header.split(" ", 1)[1]

    # Add token to blacklist
    auth_service.TOKEN_BLACKLIST.add(token)

    return {"message": "Logged out successfully"}
