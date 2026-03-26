from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.user import User, UserRole
from app.domain.order_service import OrderService
from app.domain.order_item_service import change_item_status, OrderItemDomainError
from app.schemas.order.order_item import OrderItemStatusUpdate
from app.dependencies.auth import get_current_user
from app.websocket.manager import manager

router = APIRouter(prefix="/order-items", tags=["order-items"])

@router.patch("/{item_id}/status")
async def update_item_status(
    item_id: int,
    data: OrderItemStatusUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    item = db.query(OrderItem).filter(
        OrderItem.id == item_id,
        OrderItem.restaurant_id == user.restaurant_id
    ).first()

    if not item:
        raise HTTPException(404, "Item not found")

    service = OrderService(db)

    try:
        change_item_status(item, data.status, user, service)
    except OrderItemDomainError as e:
        raise HTTPException(400, str(e))

    db.commit()
    db.refresh(item)

    # 🔔 notificación
    if item.status == OrderItemStatus.READY:
        await manager.send_to_role(
            restaurant_id=user.restaurant_id,
            role=UserRole.WAITER,
            message={
                "type": "ITEM_READY",
                "table": item.order.table.number,
                "product": item.product.name,
                "quantity": item.quantity,
                "order_id": item.order.id,
                "item_id": item.id
            }
        )

    return {
        "item_id": item.id,
        "new_status": item.status
    }