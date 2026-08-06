from sqlalchemy.orm import Session

from app.models.user import User
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product
from app.models.order import Order

from app.schemas.order.kitchen import KitchenItemOut

class KitchenService:
    """
    Servicio encargado de la lógica de negocio relacionada con la cocina.

    Responsabilidades:
    - Devolver items a pedido
    - Acceder a la base de datos mediante SQLAlchemy.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # -------------------------------------------------------------------------
    # Obtener los items de una estación, filtrando por estado y restaurante
    # -------------------------------------------------------------------------
    def get_station_items(
        self,
        station_id: int,
        user: User
    ) -> list[KitchenItemOut]:
        items = (
            self.db.query(OrderItem)
            .join(OrderItem.product)
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
            .order_by(Order.created_at, OrderItem.id)
            .all()
        )
        return [
            KitchenItemOut(
                item_id=item.id,
                product_name=item.product.name,
                quantity=item.quantity,
                status=item.status,
                table_number=item.order.table.number,
                order_id=item.order.id
            )
            for item in items
        ]