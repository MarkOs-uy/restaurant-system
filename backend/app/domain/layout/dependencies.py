from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .layout_service import LayoutService


def get_layout_service(db: Session = Depends(get_db)):
    return LayoutService(db)