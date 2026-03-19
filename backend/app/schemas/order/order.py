from decimal import Decimal
from app.models.order import OrderStatus
from ..base import BaseSchema
from .order_item import OrderItemOut
from .payment import PaymentOut


class OrderOut(BaseSchema):
    id: int
    table_number: int
    status: OrderStatus
    items: list[OrderItemOut]
    payments: list[PaymentOut]
    subtotal: float
    discount: float
    total: float
    total_paid: float
    remaining: float


class WaiterOrderOut(BaseSchema):
    id: int
    table_id: int
    table_number: int
    status: OrderStatus
    items: list[OrderItemOut]
    subtotal: float
    discount: float
    total: float
    total_paid: float
    remaining: float


class OrderStatusUpdate(BaseSchema):
    status: OrderStatus