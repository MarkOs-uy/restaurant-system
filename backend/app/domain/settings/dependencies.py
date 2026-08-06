from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .settings_service import SettingsService


def get_settings_service(
    db: Session = Depends(get_db)
) -> SettingsService:
    return SettingsService(db)