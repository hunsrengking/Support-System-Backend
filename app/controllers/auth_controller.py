# app/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.config.db import get_db
from app.services import user_service  # or your actual import
from app.services import auth_service  # if you use a shared auth_service for tokens

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = user_service.getUserByEmail(db, payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # read the stored hash from your existing column 'password'
    stored_hash = getattr(user, "password", None)
    if not stored_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # verify using same pwd_context
    if not pwd_context.verify(payload.password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    # create token (your auth_service.create_access_token or similar)
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "name": getattr(user, "username", ""),
    }
    access_token = auth_service.create_access_token(token_data)

    # don't include hashed password in response
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "username": user.username, "role_id": user.role_id},
    }
