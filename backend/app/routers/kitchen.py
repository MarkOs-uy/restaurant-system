from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.table import Table
from app.models.restaurant import Restaurant

from app.core.dependencies import get_current_restaurant

router = APIRouter(prefix="/kitchen", tags=["kitchen"])


@router.get("/stations/{station_id}/items")
def list_station_items(
    station_id: int,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    items = (
        db.query(OrderItem)
        .join(Product)
        .join(Order)
        .join(Table)
        .filter(
            Product.station_id == station_id,
            Order.restaurant_id == restaurant.id,
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
