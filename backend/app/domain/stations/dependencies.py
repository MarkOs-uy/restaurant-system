from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .station_service import StationService


def get_station_service(
    db: Session = Depends(get_db)
) -> StationService:
    return StationService(db)