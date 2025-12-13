import requests
from sqlalchemy.orm import Session
from app.schema.telegram_schema import TelegramConfig

def getActiveTelegramConfig(db: Session):
    return (
        db.query(TelegramConfig)
        .filter(TelegramConfig.is_active == True)
        .first()
    )

def SendTelegramMessageAsync(bot_token: str, chat_id: str, message: str):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }
    requests.post(url, json=payload, timeout=10)
