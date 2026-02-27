from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.table import Table
from app.models.restaurant import Restaurant
from app.models.user import User
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/kitchen", tags=["kitchen"])


@router.get("/stations/{station_id}/items")
def list_station_items(
    station_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = (
        db.query(OrderItem)
        .join(Product)
        .join(Order)
        .join(Table)
        .filter(
            Product.station_id == station_id,
            Order.restaurant_id == user.restaurant_id,
            Order.status != OrderStatus.CLOSED,
            OrderItem.status.in_([
                OrderItemStatus.SENT,
                OrderItemStatus.IN_PROGRESS,
                OrderItemStatus.READY
            ])
        )
        .all()
    )

    return [
        {
            "item_id": item.id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "status": item.status.value,
            "table_number": item.order.table.number,
            "order_id": item.order.id
        }
        for item in items
    ]
