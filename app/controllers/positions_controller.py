from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.services import positions_service
from app.models.positions_model import PositionResponse, PositionCreate, PositionUpdate

router = APIRouter(tags=["positions"])


@router.get("/positions", response_model=list[PositionResponse])
def getAllPositions(db: Session = Depends(get_db)):
    return positions_service.getAllPosition(db)


@router.post("/positions", response_model=PositionResponse)
def create_position(
    data: PositionCreate,
    db: Session = Depends(get_db),
):
    return positions_service.create_position(data, db)


@router.put("/positions/{position_id}", response_model=PositionResponse)
def update_position(
    position_id: int,
    data: PositionUpdate,
    db: Session = Depends(get_db),
):
    return positions_service.update_position(position_id, data, db)


@router.delete("/positions/{position_id}")
def delete_position(
    position_id: int,
    db: Session = Depends(get_db),
):
    return positions_service.delete_position(position_id, db)
