from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.services import report_service
from sqlalchemy import text

router = APIRouter()


@router.get("/reports-testing")
def get_reports(db: Session = Depends(get_db)):
    return db.execute(
        text("SELECT * FROM v_ticket_reports")
    ).mappings().all()

@router.get("/reports")
def get_report(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return report_service.getReports(
        db=db,
        from_date=from_date,
        to_date=to_date,
        status=status,
    )
