# schemas/waiter.py

from .base import BaseSchema

class WaiterItemOut(BaseSchema):
    id: int
    product_name: str
    quantity: int
    status: str
