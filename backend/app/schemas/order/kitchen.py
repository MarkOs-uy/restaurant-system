from app.models.order_item import OrderItemStatus
from ..base import BaseSchema

class KitchenItemOut(BaseSchema):
    item_id: int
    product_name: str
    quantity: int
    status: OrderItemStatus
    table_number: int
    order_id: int