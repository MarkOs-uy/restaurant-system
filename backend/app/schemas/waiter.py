# schemas/waiter.py

from pydantic import BaseModel
from typing import List
from decimal import Decimal

class WaiterItemOut(BaseModel):
    id: int
    product_name: str
    quantity: int
    status: str
