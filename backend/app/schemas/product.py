from decimal import Decimal
from typing import Optional
from .base import BaseSchema


class ProductCreate(BaseSchema):
    name: str
    price: Decimal
    category_id: int
    station_id: int


class ProductUpdate(BaseSchema):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    category_id: Optional[int] = None
    station_id: Optional[int] = None


class ProductOut(BaseSchema):
    id: int
    name: str
    price: Decimal
    category_id: int
    station_id: int
    active: bool


class ProductMenu(BaseSchema):
    id: int
    name: str
    price: Decimal