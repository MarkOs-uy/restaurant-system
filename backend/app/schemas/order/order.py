from decimal import Decimal
from pydantic import Field
from app.models.order import OrderStatus
from datetime import datetime
from ..base import BaseSchema
from .order_item import OrderItemOut
from .payment import PaymentOut


class OrderResponse(BaseSchema):
    id: int
    table_id: int
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

class OrderStatusUpdate(BaseSchema):
    status: OrderStatus

class OrderCancel(BaseSchema):
    reason: str = Field(
        min_length=1,
        max_length=500
    )