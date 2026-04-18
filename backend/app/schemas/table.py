from app.models.order import OrderStatus
from .base import BaseSchema
from typing import Optional
from enum import Enum

class TableStatus(str, Enum):
    FREE = "libre"
    OCCUPIED = "ocupada"

class TableOut(BaseSchema):
    id: int
    number: int
    x: int
    y: int
    capacity: int
    shape: str
    active: bool
    status: TableStatus
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


class TableList(BaseSchema):
    id: int
    number: int
    capacity: int
    shape: str
    active: bool

class TablePositionUpdate(BaseSchema):
    x: int
    y: int