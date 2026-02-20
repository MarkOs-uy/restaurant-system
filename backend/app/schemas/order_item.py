from pydantic import BaseModel
from app.models.order_item import OrderItemStatus


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderItemStatusUpdate(BaseModel):
    status: OrderItemStatus
