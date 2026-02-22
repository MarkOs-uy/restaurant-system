from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.order import Order
from app.models.product import Product
from app.models.table import Table

router = APIRouter(prefix="/kitchen", tags=["kitchen"])


@router.get("/stations/{station_id}/items")
def list_station_items(
    station_id: int,
    db: Session = Depends(get_db)
):
    """
    Devuelve los items activos de una estación.
    Solo muestra SENT e IN_PROGRESS.
    """

    items = (
        db.query(OrderItem)
        .join(Product)
        .join(Order)
        .join(Table)
        .filter(
            Product.station_id == station_id,
            Order.status != "CLOSED",
            or_(
                OrderItem.status == OrderItemStatus.SENT,
                OrderItem.status == OrderItemStatus.IN_PROGRESS,
                OrderItem.status == OrderItemStatus.READY
            )
        )
        .all()
    )

    result = []

    for item in items:
        result.append({
            "item_id": item.id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "status": item.status.value,
            "table_number": item.order.table.number,
            "order_id": item.order.id
        })

    return result
