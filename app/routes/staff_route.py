from fastapi import APIRouter
from app.controllers import staff_controller

router = APIRouter()
router.include_router(staff_controller.router, prefix="/api")
