from app.models.order import OrderStatus
from .base import BaseSchema

class TableOut(BaseSchema):
    id: int
    number: int

    x: int
    y: int
    shape: str

    status: str
    order_id: int | None
    order_status: OrderStatus | None