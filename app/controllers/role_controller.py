from fastapi import APIRouter, Depends, HTTPException, status
from app.models.role_model import RoleCreateReq, RolePermsReq
from sqlalchemy.orm import Session

from app.config.db import get_db
from app.services import role_service
from app.middlewares.auth_middlewares import requirepermissions

router = APIRouter()


@router.get("/role")
@requirepermissions("view_roles")
def listRoles(db: Session = Depends(get_db)):
    roles = role_service.getAllRole(db)
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": getattr(r, "description", None),
            "permissions": [p.name for p in getattr(r, "permissions", [])],
        }
        for r in roles
    ]


@router.get("/role/{role_id}")
@requirepermissions("view_roles")
def getRole(role_id: int, db: Session = Depends(get_db)):
    role = role_service.getRoleById(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail=f"Role with id={role_id} not found")
    return {
        "id": role.id,
        "name": role.name,
        "description": getattr(role, "description", None),
        "permissions": [p.name for p in getattr(role, "permissions", [])],
    }


@router.post("/role")
@requirepermissions("create_roles")
def createRole(date: RoleCreateReq, db: Session = Depends(get_db)):
    role = role_service.createRole(db, date.name, date.description)
    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "permissions": [],
    }


@router.put("/role/{role_id}/permissions")
@requirepermissions("edit_roles")
def updatePermissions(role_id: int, date: RolePermsReq, db: Session = Depends(get_db)):
    role = role_service.updateRolePermissions(db, role_id, date.permissions)
    return {
        "id": role.id,
        "name": role.name,
        "permissions": [p.name for p in role.permissions],
    }
