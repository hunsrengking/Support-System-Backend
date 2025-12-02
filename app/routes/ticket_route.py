from fastapi import APIRouter
from app.controllers import ticket_controller

router = APIRouter()
router.include_router(ticket_controller.router, prefix="/api")
