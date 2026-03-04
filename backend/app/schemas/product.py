from decimal import Decimal
from .base import BaseSchema

class ProductCreate(BaseSchema):
    name: str
    price: Decimal
    category_id: int
    station_id: int


class ProductOut(BaseSchema):
    id: int
    name: str
    price: Decimal
    category_id: int
    station_id: int
