from typing import List
from .base import BaseSchema
from .product import ProductOut

class CategoryOut(BaseSchema):
    id: int
    name: str
    products: list[ProductOut]