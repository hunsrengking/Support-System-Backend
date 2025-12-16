from fastapi import APIRouter
from app.controllers import positions_controller

router = APIRouter()
router.include_router(positions_controller.router, prefix="/api")
