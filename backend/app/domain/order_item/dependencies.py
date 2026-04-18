from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from .order_item_service import OrderItemService


def get_order_item_service(
    db: Session = Depends(get_db)
) -> OrderItemService:

    return OrderItemService(db)