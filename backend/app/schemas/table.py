from app.models.order import OrderStatus
from .base import BaseSchema
from typing import Optional

class TableOut(BaseSchema):
    id: int
    number: int
    x: int
    y: int
    capacity: int
    shape: str
    status: str
    order_id: int | None
    order_status: OrderStatus | None

class TableCreate(BaseSchema):
    x: int = 0
    y: int = 0
    capacity: int = 4
    shape: str = "Circular"

class TableUpdate(BaseSchema):
    number: Optional[int] = None
    capacity: Optional[int] = None
    shape: Optional[str] = None
    active: Optional[bool] = None