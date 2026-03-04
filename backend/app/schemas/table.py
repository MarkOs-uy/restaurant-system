from app.models.order import OrderStatus
from .base import BaseSchema

class TableOut(BaseSchema):
    id: int
    number: int
    status: str
    order_id: int | None
    order_status: OrderStatus | None