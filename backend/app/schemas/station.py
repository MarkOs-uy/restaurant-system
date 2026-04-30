from decimal import Decimal
from typing import Optional
from .base import BaseSchema

class StationCreate(BaseSchema):
    name: str

class StationUpdate(BaseSchema):
    name: str

class StationOut(BaseSchema):
    id: int
    name: str
    active: bool