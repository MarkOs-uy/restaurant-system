from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product
from app.models.order import Order
from app.dependencies.auth import get_current_user

from app.schemas.order.order_item import (
    OrderItemStatusUpdate,
    OrderItemOut
)
from app.schemas.order.kitchen import KitchenItemOut

from app.domain.order_item_service import (
    change_item_status,
    OrderItemDomainError
)

from app.domain.order_service import OrderService

router = APIRouter(prefix="/kitchen", tags=["kitchen"])

@router.get("/stations/{station_id}/items", response_model=list[KitchenItemOut])
def get_station_items(
    station_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = (
        db.query(OrderItem)
        .join(OrderItem.product)
        .join(Product.station)
        .join(OrderItem.order)
        .join(Order.table)
        .filter(
            Product.station_id == station_id,
            OrderItem.restaurant_id == user.restaurant_id,
            OrderItem.status.in_([
                OrderItemStatus.SENT,
                OrderItemStatus.IN_PROGRESS
            ])
        )
        .all()
    )

    result = []

    for item in items:
        result.append({
            "item_id": item.id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "status": item.status,
            "table_number": item.order.table.number,
            "order_id": item.order.id
        })

    return result


@router.patch("/{item_id}/status", response_model=OrderItemOut)
def update_item_status(
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

    try:
        change_item_status(item, data.status, user)
    except OrderItemDomainError as e:
        raise HTTPException(400, str(e))

    db.commit()
    db.refresh(item)

    return OrderItemOut(
        id=item.id,
        product_name=item.product.name,
        quantity=item.quantity,
        unit_price=item.unit_price,
        subtotal=item.quantity * item.unit_price,
        status=item.status
    )