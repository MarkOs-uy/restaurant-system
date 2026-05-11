from fastapi import APIRouter, Depends

from app.models.user import User

from app.dependencies.roles import kitchen_or_admin

from app.schemas.order.order_item import (
    OrderItemStatusUpdate,
    OrderItemOut
)
from app.schemas.order.kitchen import KitchenItemOut

from app.domain.kitchen.dependencies import get_kitchen_service
from app.domain.kitchen.kitchen_service import KitchenService


router = APIRouter(
    prefix="/kitchen",
    tags=["kitchen"]
)

# -----------------------------------------------------

@router.get(
    "/stations/{station_id}/items",
    response_model=list[KitchenItemOut]
)
def get_station_items(
    station_id: int,
    user: User = Depends(kitchen_or_admin),
    service: KitchenService = Depends(get_kitchen_service)
):
    return service.get_station_items(
        station_id=station_id,
        user=user
    )

# -----------------------------------------------------

@router.patch(
    "/{item_id}/status",
    response_model=OrderItemOut
)
def update_item_status(
    item_id: int,
    data: OrderItemStatusUpdate,
    user: User = Depends(kitchen_or_admin),
    service: KitchenService = Depends(get_kitchen_service)
):
    item = service.update_item_status(
        item_id=item_id,
        status=data.status,
        user=user
    )
    return OrderItemOut(
        id=item.id,
        product_name=item.product.name,
        quantity=item.quantity,
        unit_price=item.unit_price,
        subtotal=item.quantity * item.unit_price,
        status=item.status
    )