from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.order_item import OrderItem, OrderItemStatus
from app.schemas.order_item import OrderItemStatusUpdate

router = APIRouter(prefix="/order-items", tags=["order-items"])

ALLOWED_ITEM_TRANSITIONS = {
    OrderItemStatus.PENDING: [
        OrderItemStatus.SENT,
        OrderItemStatus.CANCELLED
    ],
    OrderItemStatus.SENT: [
        OrderItemStatus.IN_PROGRESS,
        OrderItemStatus.CANCELLED
    ],
    OrderItemStatus.IN_PROGRESS: [
        OrderItemStatus.READY,
        OrderItemStatus.CANCELLED
    ],
    OrderItemStatus.READY: [
        OrderItemStatus.DELIVERED
    ],
    OrderItemStatus.DELIVERED: [],
    OrderItemStatus.CANCELLED: []
}


@router.patch("/{item_id}/status")
def update_item_status(
    item_id: int,
    data: OrderItemStatusUpdate,
    db: Session = Depends(get_db)
):
    item = db.query(OrderItem).filter(OrderItem.id == item_id).first()

    if not item:
        raise HTTPException(404, "Item not found")

    if data.status not in ALLOWED_ITEM_TRANSITIONS[item.status]:
        raise HTTPException(
            400,
            f"Invalid transition from {item.status} to {data.status}"
        )

    item.status = data.status
    db.commit()
    db.refresh(item)

    return {
        "item_id": item.id,
        "new_status": item.status
    }