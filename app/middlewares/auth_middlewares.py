import inspect
from functools import wraps
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.services import auth_service, user_service, role_service
import logging

auth_scheme = HTTPBearer(auto_error=False)


# def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
#     db: Session = Depends(get_db),
# ):
#     if credentials is None or not credentials.credentials:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
#         )
#     token = credentials.credentials
#     payload = auth_service.decode_access_token(token)
#     user_id = payload.get("sub")
#     if not user_id:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
#         )
#     user = user_service.getUserById(db, int(user_id))
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
#         )
#     return user

logger = logging.getLogger("app.auth")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_db),
):
    if credentials is None or not credentials.credentials:
        logger.debug("No Authorization header provided.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated: Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = auth_service.decode_access_token(token)
    except Exception as e:
        # decode_access_token typically raises on invalid/expired token
        logger.warning("Token decode failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not payload:
        logger.warning("Token decode returned empty payload.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3) Ensure 'sub' present (or the claim name you use)
    user_id = payload.get("sub")
    if not user_id:
        logger.warning("Token payload missing 'sub': %s", payload)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4) Retrieve user from DB
    try:
        user = user_service.getUserById(db, int(user_id))
    except Exception as e:
        logger.error("Error fetching user from DB (id=%s): %s", user_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    if not user:
        logger.info("User not found for id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def requirepermissions(permission_name: str):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(
            *args, current_user=Depends(get_current_user), **kwargs
        ):
            role = getattr(current_user, "role", None)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="No role assigned"
                )
            user_permissions = [p.name for p in getattr(role, "permissions", [])]
            if permission_name not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
                )
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, current_user=Depends(get_current_user), **kwargs):
            role = getattr(current_user, "role", None)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="No role assigned"
                )
            user_permissions = [p.name for p in getattr(role, "permissions", [])]
            if permission_name not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
                )
            return func(*args, **kwargs)

        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator
