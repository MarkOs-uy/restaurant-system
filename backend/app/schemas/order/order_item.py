from decimal import Decimal
from app.models.order_item import OrderItemStatus
from ..base import BaseSchema
from pydantic import Field

class OrderItemCreate(BaseSchema):
    product_id: int
    quantity: int
    notes: str | None = None


class OrderItemStatusUpdate(BaseSchema):
    status: OrderItemStatus


class OrderItemOut(BaseSchema):
    id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    status: OrderItemStatus
    notes: str | None = None

class OrderItemCancel(BaseSchema):
    reason: str = Field(
        min_length=1,
        max_length=500
    )