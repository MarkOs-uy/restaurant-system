from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .table_service import TableService


def get_table_service(db: Session = Depends(get_db)):
    return TableService(db)