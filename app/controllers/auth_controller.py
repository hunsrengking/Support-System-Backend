# app/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config.db import get_db
from app.services import auth_service

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.LoginService(
        db=db,
        email=payload.email,
        password=payload.password,
    )


@router.post("/logout")
def logout(request: Request):
    auth_header = request.headers.get("authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Missing Authorization")

    token = auth_header.split(" ", 1)[1]
    auth_service.LogoutService(token)

    return {"message": "Logged out successfully"}
