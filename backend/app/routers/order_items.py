from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.production_station import ProductionStation
from app.models.order_item import OrderItem, OrderItemStatus

router = APIRouter(prefix="/order_items", tags=["order_items"])

@router.patch("/order-items/{item_id}/status")
def update_item_status(
    item_id: int,
    status: OrderItemStatus,
    db: Session = Depends(get_db)
):
    item = db.query(OrderItem).filter(OrderItem.id == item_id).first()

    if not item:
        raise HTTPException(404, "Item not found")

    item.status = status
    db.commit()
    db.refresh(item)

    return item
