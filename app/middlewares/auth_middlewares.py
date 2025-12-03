import inspect
from functools import wraps
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.services import auth_service, user_service,role_service


auth_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_db),
):
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    token = credentials.credentials
    payload = auth_service.decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )
    user = user_service.getUserById(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
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
            # call original (it might be sync or async)
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

        # Return an async wrapper if original is async, else sync wrapper.
        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator
