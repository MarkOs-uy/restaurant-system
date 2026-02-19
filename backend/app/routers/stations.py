from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.production_station import ProductionStation
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product

router = APIRouter(prefix="/stations", tags=["stations"])

@router.get("/stations/{station_id}/items")
def get_station_items(station_id: int, db: Session = Depends(get_db)):
    items = (
        db.query(OrderItem)
        .join(Product)
        .filter(
            Product.station_id == station_id,
            OrderItem.status.in_([
                OrderItemStatus.SENT,
                OrderItemStatus.IN_PROGRESS
            ])
        )
        .all()
    )

    return items
