from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schema.role_schema import Role
from app.schema.permission_schema import Permission


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
        result = db.query(Role).filter(Role.id == role_id).update({"is_active": 0})
        if result == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
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
