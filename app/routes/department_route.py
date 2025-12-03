from fastapi import APIRouter
from app.controllers import department_controller

router = APIRouter()
router.include_router(department_controller.router, prefix="/api")
