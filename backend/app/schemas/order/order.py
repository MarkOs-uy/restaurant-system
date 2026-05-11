from decimal import Decimal
from app.models.order import OrderStatus
from ..base import BaseSchema
from .order_item import OrderItemOut
from .payment import PaymentOut


class OrderOut(BaseSchema):
    id: int
    table_number: int
    status: OrderStatus
    created_at: str
    items: list[OrderItemOut]
    payments: list[PaymentOut]
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    total_paid: Decimal
    remaining: Decimal


class WaiterOrderOut(BaseSchema):
    id: int
    table_id: int
    table_number: int
    status: OrderStatus
    created_at: str
    items: list[OrderItemOut]
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    total_paid: Decimal
    remaining: Decimal


class OrderStatusUpdate(BaseSchema):
    status: OrderStatus