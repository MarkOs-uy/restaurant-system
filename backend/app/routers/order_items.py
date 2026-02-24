from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.restaurant import Restaurant
from app.models.user import User, UserRole
from app.schemas.order_item import OrderItemStatusUpdate
from app.dependencies.auth import get_current_user
from app.core.dependencies import get_current_restaurant

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
    user: User = Depends(get_current_user),
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    item = db.query(OrderItem).filter(
        OrderItem.id == item_id,
        OrderItem.restaurant_id == user.restaurant_id
    ).first()

    if not item:
        raise HTTPException(404, "Item not found")

    # 🔐 CONTROL POR ROL

    if data.status == OrderItemStatus.IN_PROGRESS and user.role != UserRole.KITCHEN:
        raise HTTPException(403, "Only kitchen can start items")

    if data.status == OrderItemStatus.READY and user.role != UserRole.KITCHEN:
        raise HTTPException(403, "Only kitchen can mark ready")

    if data.status == OrderItemStatus.DELIVERED and user.role != UserRole.WAITER:
        raise HTTPException(403, "Only waiter can deliver")


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
