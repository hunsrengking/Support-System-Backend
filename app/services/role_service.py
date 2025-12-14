from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schema.role_schema import Role, role_permissions
from app.schema.user_schema import User
from app.schema.permission_schema import Permission
from fastapi import HTTPException, status
from sqlalchemy import exists


def getAllRole(db: Session) -> List[Role]:
    return db.query(Role).filter(Role.is_active == 1).all()


def getRoleById(db: Session, role_id: int) -> Role | None:
    return db.query(Role).filter(Role.id == role_id).first()


def createRole(db: Session, name: str, description: str | None = None) -> Role:
    name = name.strip()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Role name required"
        )

    existing = db.query(Role).filter(Role.name == name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this name already exists",
        )

    role = Role(name=name, description=description)
    try:
        db.add(role)
        db.commit()
        db.refresh(role)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create role",
        )

    return role


def disableRole(db: Session, role_id: int) -> None:
    try:
        # Check if role exists and is active
        role = db.query(Role).filter(Role.id == role_id, Role.is_active == 1).first()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found or already disabled",
            )

        # Check if role has active users
        has_active_users = db.query(
            exists().where(User.role_id == role_id, User.is_active == 1)
        ).scalar()

        if has_active_users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot disable role with active users",
            )

        # Disable role
        role.is_active = 0  # type: ignore
        db.commit()

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not disable role",
        )


def getAllPermissions(db: Session) -> List[Permission]:
    return db.query(Permission).all()


def getPermissionByRoleId(db: Session, role_id: int) -> List[str]:
    rows = (
        db.query(Permission.name, Permission.group)
        .join(role_permissions, Permission.id == role_permissions.c.permission_id)
        .filter(role_permissions.c.role_id == role_id)
        .all()
    )
    return [r[0] for r in rows]


def getPermissionByUserId(db: Session, user_id: int) -> List[str]:
    rows = (
        db.query(Permission.name)
        .join(role_permissions, Permission.id == role_permissions.c.permission_id)
        .join(Role, Role.id == role_permissions.c.role_id)
        .join(User, User.role_id == Role.id)
        .filter(User.id == user_id, User.is_delete == 0)
        .distinct()
        .all()
    )
    return [r[0] for r in rows]


def updateRolePermissionsById(
    db: Session, role_id: int, permission_ids: List[int]
) -> Role:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    ids = [int(i) for i in permission_ids if i is not None]

    if not ids:
        role.permissions = []
        db.add(role)
        try:
            db.commit()
            db.refresh(role)
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear role permissions",
            )
        return role

    # fetch all Permission rows matching the ids in bulk
    perms = db.query(Permission).filter(Permission.id.in_(ids)).all()

    found_ids = {p.id for p in perms}
    missing = [i for i in ids if i not in found_ids]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Permission(s) not found: {missing}",
        )

    try:
        role.permissions = perms
        db.add(role)
        db.commit()
        db.refresh(role)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update role permissions",
        )

    return role
