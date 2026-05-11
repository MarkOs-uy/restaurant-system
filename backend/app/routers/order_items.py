from fastapi import APIRouter, Depends

from app.models.user import User, UserRole

from app.dependencies.roles import waiter_kitchen_or_admin

from app.schemas.order.order_item import OrderItemStatusUpdate

from app.domain.order_item.order_item_service import OrderItemService
from app.domain.order_item.dependencies import get_order_item_service

router = APIRouter(
    prefix="/order-items",
    tags=["order-items"]
)

@router.patch("/{item_id}/status")
async def update_item_status(
    item_id: int,
    data: OrderItemStatusUpdate,
    user: User = Depends(waiter_kitchen_or_admin),
    service: OrderItemService = Depends(get_order_item_service)
):
    return service.update_status(
        item_id=item_id,
        new_status=data.status,
        user=user
    )