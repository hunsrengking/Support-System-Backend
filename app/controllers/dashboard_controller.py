from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.services import dashboard_service

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    return dashboard_service.get_summary(db)

@router.get("/dashboard/ticketsbydate")
def tickets_by_date(db: Session = Depends(get_db)):
    return dashboard_service.tickets_by_date(db)


@router.get("/dashboard/ticketsbymonth")
def tickets_by_month(db: Session = Depends(get_db)):
    return dashboard_service.tickets_by_month(db)