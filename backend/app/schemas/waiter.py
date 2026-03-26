# schemas/waiter.py

from pydantic import BaseModel

class WaiterItemOut(BaseModel):
    id: int
    product_name: str
    quantity: int
    status: str
