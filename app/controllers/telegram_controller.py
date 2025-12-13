from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.schema.telegram_schema import TelegramConfig
from app.models.telegram_model import (
    TelegramConfigCreate,
    TelegramConfigUpdate,
    TelegramConfigResponse,
)

router = APIRouter(tags=["Telegram"])

@router.get("/telegram", response_model=list[TelegramConfigResponse])
def list_configs(db: Session = Depends(get_db)):
    return db.query(TelegramConfig).all()


@router.post("/telegram", response_model=TelegramConfigResponse)
def create_config(data: TelegramConfigCreate, db: Session = Depends(get_db)):
    # disable others
    if data.is_active:
        db.query(TelegramConfig).update({"is_active": False})

    config = TelegramConfig(**data.dict())
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.put("/{config_id}", response_model=TelegramConfigResponse)
def update_config(
    config_id: int,
    data: TelegramConfigUpdate,
    db: Session = Depends(get_db),
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


@router.delete("/{config_id}")
def delete_config(config_id: int, db: Session = Depends(get_db)):
    config = db.query(TelegramConfig).filter_by(id=config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    db.delete(config)
    db.commit()
    return {"message": "Deleted successfully"}
