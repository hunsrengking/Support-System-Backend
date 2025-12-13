from fastapi import APIRouter
from app.controllers import telegram_controller

router = APIRouter()
router.include_router(telegram_controller.router, prefix="/api")
