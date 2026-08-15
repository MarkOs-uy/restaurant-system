from app.models.order import OrderStatus
from .base import BaseSchema
from app.models.enums import TableShape

class TableCreate(BaseSchema):
    number: int | None = None
    x: int = 0
    y: int = 0
    capacity: int = 4
    shape: TableShape = TableShape.CIRCLE

class TableResponse(BaseSchema):
    id: int
    number: int
    x: int
    y: int
    capacity: int
    shape: TableShape
    active: bool

class TableUpdate(BaseSchema):
    number: int | None = None
    capacity: int | None = None
    shape: TableShape | None = None
    active: bool | None = None

class TableStatusResponse(BaseSchema):
    id: int
    number: int
    x: int
    y: int
    capacity: int
    shape: TableShape
    active: bool
    order_id: int | None
    order_status: OrderStatus | None

class TableList(BaseSchema):
    id: int
    number: int
    capacity: int
    shape: TableShape
    active: bool

class TablePositionUpdate(BaseSchema):
    x: int
    y: int

class TablePositionOut(BaseSchema):
    id: int
    x: int
    y: int

class TableTouchResponse(BaseSchema):
    table_id: int
    table_number: int
    order_id: int | None