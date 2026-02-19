from pydantic import BaseModel
from app.models.order import OrderStatus
from typing import List
from decimal import Decimal

ALLOWED_TRANSITIONS = {
    OrderStatus.OPEN: [OrderStatus.SENT, OrderStatus.CANCELLED],
    OrderStatus.SENT: [OrderStatus.IN_PROGRESS],
    OrderStatus.IN_PROGRESS: [OrderStatus.READY],
    OrderStatus.READY: [OrderStatus.CLOSED],
}

class OrderItemOut(BaseModel):
    id: int
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float
    status: str
#class OrderItemOut(BaseModel):
#    product_name: str
#    quantity: int
#    unit_price: Decimal

class OrderOut(BaseModel):
    order_id: int
    table_number: int
    status: str
    items: List[OrderItemOut]
    total: Decimal

class OrderStatusUpdate(BaseModel):
    status: OrderStatus