from decimal import Decimal
from app.models.order_item import OrderItemStatus
from ..base import BaseSchema

class OrderItemCreate(BaseSchema):
    product_id: int
    quantity: int


class OrderItemStatusUpdate(BaseSchema):
    status: OrderItemStatus


class OrderItemOut(BaseSchema):
    id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    status: OrderItemStatus