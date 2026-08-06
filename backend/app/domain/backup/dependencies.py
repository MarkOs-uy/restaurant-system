from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .backup_service import BackupService


def get_backup_service(
    db: Session = Depends(get_db)
) -> BackupService:
    return BackupService(db)