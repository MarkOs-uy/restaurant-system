from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product
from app.models.production_station import ProductionStation
from app.models.user import User
from app.models.order import Order


from app.schemas.order.kitchen import KitchenItemOut

from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/stations", tags=["stations"])

@router.get("/")
def list_stations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return db.query(ProductionStation).filter(
        ProductionStation.restaurant_id == user.restaurant_id
    ).order_by(ProductionStation.name).all()


@router.post("/")
def create_station(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    station = ProductionStation(
        name=data["name"],
        restaurant_id=user.restaurant_id,
        active=True
    )

    db.add(station)
    db.commit()
    db.refresh(station)

    return station


@router.patch("/{station_id}")
def update_station(
    station_id: int,
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    station = db.query(ProductionStation).filter(
        ProductionStation.id == station_id,
        ProductionStation.restaurant_id == user.restaurant_id
    ).first()

    if not station:
        raise HTTPException(404, "Station not found")

    station.name = data["name"]

    db.commit()
    db.refresh(station)

    return station


@router.patch("/{station_id}/toggle")
def toggle_station(
    station_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    station = db.query(ProductionStation).filter(
        ProductionStation.id == station_id,
        ProductionStation.restaurant_id == user.restaurant_id
    ).first()

    if not station:
        raise HTTPException(404, "Station not found")

    station.active = not station.active

    db.commit()
    db.refresh(station)

    return station

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

@router.get("/active")
def list_active_stations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    stations = db.query(ProductionStation).filter(
        ProductionStation.restaurant_id == user.restaurant_id,
        ProductionStation.active == True
    ).order_by(ProductionStation.name).all()

    return stations


@router.get("/{station_id}")
def get_station(
    station_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    station = db.query(ProductionStation).filter(
        ProductionStation.id == station_id,
        ProductionStation.restaurant_id == user.restaurant_id
    ).first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    return station