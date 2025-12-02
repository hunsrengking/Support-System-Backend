# app/services/role_service.py
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schema.role_schema import Role
from app.schema.permission_schema import Permission

def getAllRole(db: Session) -> List[Role]:
    return db.query(Role).all()


def getRoleById(db: Session, role_id: int) -> Role | None:
    return db.query(Role).filter(Role.id == role_id).first()


def createRole(db: Session, name: str, description: str | None = None) -> Role:
    name = name.strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role name required")

    existing = db.query(Role).filter(Role.name == name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role with this name already exists")

    role = Role(name=name, description=description)
    try:
        db.add(role)
        db.commit()
        db.refresh(role)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create role")

    return role


def updateRolePermissions(db: Session, role_id: int, permission_names: List[str]) -> Role:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    permissions = []
    for raw in permission_names:
        if raw is None:
            continue
        pname = raw.strip()
        if not pname:
            continue
        perm = db.query(Permission).filter(Permission.name == pname).first()
        if not perm:
            perm = Permission(name=pname)
            db.add(perm)
            try:
                db.commit()
                db.refresh(perm)
            except Exception:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create permission '{pname}'")
        permissions.append(perm)
    try:
        role.permissions = permissions
        db.add(role)
        db.commit()
        db.refresh(role)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update role permissions")

    return role
