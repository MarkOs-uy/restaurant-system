from decimal import Decimal
from .base import BaseSchema
from .category import CategoryRef
from .station import StationRef

class ProductCreate(BaseSchema):
    name: str
    price: Decimal
    category_id: int
    station_id: int

class ProductUpdate(BaseSchema):
    name: str | None = None
    price: Decimal | None = None
    category_id: int | None = None
    station_id: int | None = None

class ProductResponse(BaseSchema):
    id: int
    name: str
    price: Decimal
    category_id: int
    station_id: int
    active: bool
    category: CategoryRef
    station: StationRef