from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies.roles import admin_only
from app.domain.backup.backup_service import BackupService
from app.models.user import User


router = APIRouter(prefix="/backups", tags=["backups"])


class BackupEmailRequest(BaseModel):
    email: str


@router.get("/status")
def backup_status(user: User = Depends(admin_only)):
    return BackupService().status()


@router.post("")
def create_backup(user: User = Depends(admin_only)):
    try:
        return BackupService().create_backup()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/email")
def create_and_email_backup(
    data: BackupEmailRequest,
    user: User = Depends(admin_only)
):
    if "@" not in data.email or "." not in data.email:
        raise HTTPException(status_code=400, detail="Correo electronico invalido")

    try:
        return BackupService().create_and_email_backup(data.email)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
