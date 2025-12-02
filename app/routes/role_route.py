from fastapi import APIRouter
from app.controllers import role_controller

router = APIRouter()
router.include_router(role_controller.router, prefix="/api")
