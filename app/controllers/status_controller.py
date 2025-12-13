from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.services import status_service

router = APIRouter()


@router.get("/status")
def getAllStatus(db: Session = Depends(get_db)):
    return status_service.getAllStatus(db)

@router.get("/category")
def getAllCategory(db: Session = Depends(get_db)):
    return status_service.getAllCategory(db)

@router.get("/priority")
def getAllPriority(db: Session = Depends(get_db)):
    return status_service.getAllPriority(db)