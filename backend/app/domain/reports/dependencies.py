from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .report_service import ReportService


def get_report_service(
    db: Session = Depends(get_db)
) -> ReportService:
    return ReportService(db)
