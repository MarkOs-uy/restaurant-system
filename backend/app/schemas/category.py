from decimal import Decimal
from pydantic import Field
from .base import BaseSchema

class ProductRef(BaseSchema):
    id: int
    name: str
    price: Decimal

class CategoryCreate(BaseSchema):
    name: str

class CategoryUpdate(BaseSchema):
    name: str

class CategoryRef(BaseSchema):
    id: int
    name: str

class CategoryResponse(CategoryRef):
    active: bool

class CategoryWithProducts(CategoryResponse):
    products: list[ProductRef] = Field(default_factory=list)