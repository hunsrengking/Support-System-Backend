from fastapi import APIRouter
from app.controllers import status_controller

router = APIRouter()
router.include_router(status_controller.router, prefix="/api")
