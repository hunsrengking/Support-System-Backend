import requests
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schema.telegram_schema import TelegramConfig
from app.models.telegram_model import (
    TelegramConfigCreate,
    TelegramConfigUpdate,
)


def getActiveTelegramConfig(db: Session):
    return db.query(TelegramConfig).filter(TelegramConfig.is_active == True).first()


def SendTelegramMessageAsync(bot_token: str, chat_id: str, message: str):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }
    requests.post(url, json=payload, timeout=10)


def list_configs(db: Session):
    return db.query(TelegramConfig).all()


def create_config(data: TelegramConfigCreate, db: Session):
    # Only one active config allowed
    if data.is_active:
        db.query(TelegramConfig).update({"is_active": False})

    config = TelegramConfig(**data.dict())
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


def update_config(
    config_id: int,
    data: TelegramConfigUpdate,
    db: Session,
):
    config = db.query(TelegramConfig).filter_by(id=config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    if data.is_active:
        db.query(TelegramConfig).update({"is_active": False})

    for key, value in data.dict(exclude_unset=True).items():
        setattr(config, key, value)

    db.commit()
    db.refresh(config)
    return config


def delete_config(config_id: int, db: Session):
    config = db.query(TelegramConfig).filter_by(id=config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    db.delete(config)
    db.commit()
    return {"message": "Deleted successfully"}
