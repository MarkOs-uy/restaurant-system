from sqlalchemy.orm import Session, joinedload
from app.models.production_station import ProductionStation

from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product
from app.models.order import Order

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode


class StationService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Crear estación
    # ------------------------- 

    def create_station(self, restaurant_id: int, name: str):
        existing = (
            self.db.query(ProductionStation)
            .filter(
                ProductionStation.restaurant_id == restaurant_id,
                ProductionStation.name == name
            )
            .first()
        )
        if existing:
            raise DomainError(
                "Station name already exists",
                code=ErrorCode.STATION_NAME_ALREADY_EXISTS,
                context={"name": name}
            )
        station = ProductionStation(
            name=name,
            restaurant_id=restaurant_id,
            active=True
        )
        self.db.add(station)
        self.db.commit()
        self.db.refresh(station)
        return station
    
    # -------------------------
    # Listar estaciones
    # -------------------------

    def list_stations(self, restaurant_id: int):
        return (
            self.db.query(ProductionStation)
            .filter(ProductionStation.restaurant_id == restaurant_id)
            .order_by(ProductionStation.name)
            .all()
        )

    # -------------------------
    # Listar estaciones activas
    # -------------------------

    def list_active_stations(self, restaurant_id: int):
        return (
            self.db.query(ProductionStation)
            .filter(
                ProductionStation.restaurant_id == restaurant_id,
                ProductionStation.active.is_(True)
            )
            .order_by(ProductionStation.name)
            .all()
        )

    # -------------------------
    # Obtener estación
    # -------------------------

    def get_station(self, restaurant_id: int, station_id: int):
        station = (
            self.db.query(ProductionStation)
            .filter(
                ProductionStation.id == station_id,
                ProductionStation.restaurant_id == restaurant_id
            )
            .first()
        )
        if not station:
            raise DomainError(
                "Station not found",
                code=ErrorCode.STATION_NOT_FOUND
            )
        return station

    # -------------------------
    # Actualizar estación
    # -------------------------

    def update_station(self, restaurant_id: int, station_id: int, name: str):
        station = self.get_station(restaurant_id, station_id)
        existing = (
            self.db.query(ProductionStation)
            .filter(
                ProductionStation.restaurant_id == restaurant_id,
                ProductionStation.name == name,
                ProductionStation.id != station_id
            )
            .first()
        )
        if existing:
            raise DomainError(
                "Station name already exists",
                code=ErrorCode.STATION_NAME_ALREADY_EXISTS
            )
        station.name = name
        self.db.commit()
        self.db.refresh(station)
        return station

    # -------------------------
    # Activar/desactivar estación
    # -------------------------

    def toggle_station(self, restaurant_id: int, station_id: int):
        station = self.get_station(restaurant_id, station_id)
        station.active = not station.active
        self.db.commit()
        self.db.refresh(station)
        return station

    # -------------------------
    # Para cambiar a otro service a la brevedad
    # -------------------------

    def get_station_items(self, restaurant_id: int, station_id: int):
        items = (
            self.db.query(OrderItem)
            .join(OrderItem.product)
            .join(Product.station)
            .join(OrderItem.order)
            .join(Order.table)
            .filter(
                Product.station_id == station_id,
                OrderItem.restaurant_id == restaurant_id,
                OrderItem.status.in_([
                    OrderItemStatus.SENT,
                    OrderItemStatus.IN_PROGRESS
                ])
            )
            .order_by(Order.created_at)
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