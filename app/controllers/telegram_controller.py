from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.schema.telegram_schema import TelegramConfig
from app.models.telegram_model import (
    TelegramConfigResponse,
    TelegramConfigCreate,
    TelegramConfigUpdate,
)
from app.services import telegram_service

router = APIRouter(tags=["Telegram"])


@router.get("/telegram", response_model=list[TelegramConfigResponse])
def list_configs(db: Session = Depends(get_db)):
    return telegram_service.list_configs(db)


@router.post("/telegram", response_model=TelegramConfigResponse)
def create_config(
    data: TelegramConfigCreate,
    db: Session = Depends(get_db),
):
    return telegram_service.create_config(data, db)


@router.put("/telegram/{config_id}", response_model=TelegramConfigResponse)
def update_config(
    config_id: int,
    data: TelegramConfigUpdate,
    db: Session = Depends(get_db),
):
    return telegram_service.update_config(config_id, data, db)


@router.delete("/telegram/{config_id}")
def delete_config(
    config_id: int,
    db: Session = Depends(get_db),
):
    return telegram_service.delete_config(config_id, db)
