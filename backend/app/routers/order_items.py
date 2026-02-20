from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.production_station import ProductionStation
from app.models.order_item import OrderItem, OrderItemStatus
from app.schemas.order_item import OrderItemStatusUpdate

router = APIRouter(prefix="/order_items", tags=["order_items"])

@router.patch("/order-items/{item_id}/status")
def update_item_status(
    item_id: int,
    data: OrderItemStatusUpdate,
    db: Session = Depends(get_db)
):
    item = db.query(OrderItem).filter(OrderItem.id == item_id).first()

    if not item:
        raise HTTPException(404, "Item not found")

    item.status = data.status
    db.commit()
    db.refresh(item)

    return {"id": item.id, "new_status": item.status}