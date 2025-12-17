from fastapi import APIRouter
from app.controllers import report_controller

router = APIRouter()
router.include_router(report_controller.router, prefix="/api")
