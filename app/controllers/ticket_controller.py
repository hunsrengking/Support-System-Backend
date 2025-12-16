# app/controllers/ticket_controller.py
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    UploadFile,
    File,
)
from sqlalchemy.orm import Session
from app.config.db import get_db
from app.services import ticket_service
from app.models.ticket_model import (
    TicketCreateReq,
    TicketResp,
    ApproveReq,
    TicketUpdateReq,
)
from app.middlewares.auth_middlewares import get_current_user
from app.schema.user_schema import User
import os, uuid
from fastapi.responses import FileResponse

UPLOAD_IMAGE_DIR = "app/uploads/tickets/images"
UPLOAD_FILE_DIR = "app/uploads/tickets/files"

router = APIRouter(tags=["tickets"])


@router.get("/ticket")
def ListAllTicket(db: Session = Depends(get_db)):
    return ticket_service.getAllTicket(db)


@router.get("/ticket/{id}")
def getTicketById(id: int, db: Session = Depends(get_db)):
    ticket = ticket_service.getTicketById(db, id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with id={id} not found",
        )
    return ticket


@router.get("/ticket/status/waitingapprove")
def getTicketByStatus(db: Session = Depends(get_db)):
    return ticket_service.getTicketByStautus(db)


@router.post("/ticket", response_model=TicketResp)
def CreateTicket(
    data: TicketCreateReq,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ticket_service.createTicket(
        db=db,
        data=data,
        user_id=current_user.id,  # type: ignore
        background_tasks=background_tasks,  # type: ignore
    )  # type: ignore


@router.patch("/ticket/{ticket_id}", response_model=TicketResp)
def UpdateTicket(
    ticket_id: int,
    data: TicketUpdateReq,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ticket_service.UpdateTicket(
        db=db,
        ticket_id=ticket_id,
        data=data,
        user_id=current_user.id,  # type: ignore
        background_tasks=background_tasks,
    )


@router.patch("/ticket/{id}/approve")
def ApproveTicket(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ticket_service.ApproveTicket(id=id, db=db, user_id=current_user.id)  # type: ignore


@router.patch("/ticket/{id}/reject")
def RejectTicket(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ticket_service.RejectTicket(id=id, db=db, user_id=current_user.id)  # type: ignore


@router.delete("/ticket/{id}")
def DeleteTicket(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ticket_service.DeleteTicket(id=id, db=db, user_id=current_user.id)  # type: ignore


@router.post("/ticket/upload")
def upload_ticket_file(
    image: UploadFile | None = File(None),
    file: UploadFile | None = File(None),
):
    os.makedirs(UPLOAD_IMAGE_DIR, exist_ok=True)
    os.makedirs(UPLOAD_FILE_DIR, exist_ok=True)

    result = {}

    if image:
        ext = image.filename.split(".")[-1]  # type: ignore
        image_name = f"{uuid.uuid4()}.{ext}"
        image_path = f"{UPLOAD_IMAGE_DIR}/{image_name}"

        with open(image_path, "wb") as f:
            f.write(image.file.read())

        result["image_path"] = image_path

    if file:
        ext = file.filename.split(".")[-1]  # type: ignore
        file_name = f"{uuid.uuid4()}.{ext}"
        file_path = f"{UPLOAD_FILE_DIR}/{file_name}"

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        result["file_path"] = file_path

    return result


@router.get("/ticket/file/download")
def download_ticket_file(path: str):
    # DB stores: app/uploads/...
    real_path = path.replace("app/", "")

    real_path = os.path.join("app", real_path)

    if not os.path.exists(real_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        real_path,
        filename=os.path.basename(real_path),
        media_type="application/octet-stream",
    )
