from typing import List
from .base import BaseSchema
from .product import ProductOut

class CategoryBase(BaseSchema):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseSchema):
    name: str


class CategoryResponse(CategoryBase):
    id: int


class CategoryWithProducts(CategoryResponse):
    products: List[ProductOut] = []