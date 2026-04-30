from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.kitchen.kitchen_service import KitchenService


def get_kitchen_service(
    db: Session = Depends(get_db)
) -> KitchenService:
    return KitchenService(db)