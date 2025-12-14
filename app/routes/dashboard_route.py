from fastapi import APIRouter
from app.controllers import dashboard_controller

router = APIRouter()
router.include_router(dashboard_controller.router, prefix="/api")
