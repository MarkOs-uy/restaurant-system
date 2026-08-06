from decimal import Decimal
from app.models.order import OrderStatus
from datetime import datetime
from ..base import BaseSchema
from .order_item import OrderItemOut
from .payment import PaymentOut


class OrderDetail(BaseSchema):
    id: int
    table_number: int
    status: OrderStatus
    created_at: datetime
    items: list[OrderItemOut]
    payments: list[PaymentOut]
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    total_paid: Decimal
    remaining: Decimal

class OrderResponse(OrderDetail):
    table_id: int

class OrderStatusUpdate(BaseSchema):
    status: OrderStatus