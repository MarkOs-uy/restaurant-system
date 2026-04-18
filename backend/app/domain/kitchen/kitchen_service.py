from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product
from app.models.order import Order

from app.schemas.order.kitchen import KitchenItemOut

from app.domain.order_item.order_item_service import OrderItemService


class KitchenService:

    def __init__(self, db: Session):
        self.db = db
        self.item_service = OrderItemService(db)

    # ----------------------------------------

    def get_station_items(
        self,
        station_id: int,
        user: User
    ) -> list[KitchenItemOut]:

        items = (
            self.db.query(OrderItem)
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
            result.append(
                KitchenItemOut(
                    item_id=item.id,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    status=item.status,
                    table_number=item.order.table.number,
                    order_id=item.order.id
                )
            )

        return result

    # ----------------------------------------

    def update_item_status(
        self,
        item_id: int,
        status: OrderItemStatus,
        user: User
    ):

        return OrderItemService.update_status(
            item_id=item_id,
            new_status=status,
            user=user
        )