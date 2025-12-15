# app/services/auth_service.py
import os
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.services import user_service

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

TOKEN_BLACKLIST = set()


# -------------------------
# Password helpers
# -------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# -------------------------
# JWT helpers
# -------------------------
def create_access_token(
    data: Dict[str, Any],
    expires_minutes: Optional[int] = None,
) -> str:
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + timedelta(minutes=(expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"iat": now, "exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    if token in TOKEN_BLACKLIST:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


# -------------------------
# AUTH BUSINESS LOGIC
# -------------------------
# def LoginService(db: Session, email: str, password: str) -> Dict[str, Any]:
#     user = user_service.getUserByEmail(db, email)

#     if not user or not getattr(user, "password", None):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials",
#         )

#     if not verify_password(password, user.password): # type: ignore
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid credentials",
#         )

#     role_data = None
#     permissions_list = []

#     if user.role:
#         role_data = {
#             "id": user.role.id,
#             "name": user.role.name,
#         }

#         permissions_list = [
#             {"id": p.id, "name": p.name}
#             for p in (user.role.permissions or [])
#         ]

#     token_payload = {
#         "sub": str(user.id),
#         "email": user.email,
#         "name": user.username,
#         "role_id": user.role_id,
#         "role": role_data,
#         "permissions": permissions_list,
#     }

#     access_token = create_access_token(token_payload)

#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "user": {
#             "id": user.id,
#             "email": user.email,
#             "username": user.username,
#             "role_id": user.role_id,
#             "role": role_data,
#             "permissions": permissions_list,
#         },
#     }


def LoginService(db: Session, email: str, password: str) -> Dict[str, Any]:
    user = user_service.getUserByEmail(db, email)

    if not user or not getattr(user, "password", None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials",
        )

    # 🔒 Check lock
    if getattr(user, "is_locked", 0) == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is locked, please contact administrator",
        )

    if not verify_password(password, user.password):  # type: ignore
        user.failed_attempts = (user.failed_attempts or 0) + 1 # type: ignore

        if user.failed_attempts >= 3: # pyright: ignore[reportGeneralTypeIssues]
            user.is_locked = 1 # type: ignore
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is locked, please contact administrator",
            )

        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials",
        )

    user.failed_attempts = 0 # type: ignore
    db.commit()

    role_data = None
    permissions_list = []

    if user.role:
        role_data = {
            "id": user.role.id,
            "name": user.role.name,
        }

        permissions_list = [
            {"id": p.id, "name": p.name} for p in (user.role.permissions or [])
        ]

    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.username,
        "role_id": user.role_id,
        "role": role_data,
        "permissions": permissions_list,
    }

    access_token = create_access_token(token_payload)

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


def LogoutService(token: str) -> Dict[str, str]:
    TOKEN_BLACKLIST.add(token)
    return {"message": "Logged out successfully"}
