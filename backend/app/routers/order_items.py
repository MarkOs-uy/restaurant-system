"""
Endpoints para la gestión de los items de una orden.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import APIRouter, Depends, status

from app.dependencies.roles import waiter_kitchen_or_admin

from app.domain.order_item.order_item_service import OrderItemService
from app.domain.order_item.dependencies import get_order_item_service

from app.models.user import User

from app.schemas.order.order_item import (
    OrderItemStatusUpdate,
    OrderItemOut
)

router = APIRouter(
    prefix="/order-items",
    tags=["order-items"]
)

# ----------------------------------------------------------------------------------------------------
# Cambiar estado de item
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{item_id}/status",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Actualizar estado de item",
    description="Actualiza el estado del item especificado."
)
def update_item_status(
    item_id: int,
    data: OrderItemStatusUpdate,
    user: User = Depends(waiter_kitchen_or_admin),
    service: OrderItemService = Depends(get_order_item_service),
):
    service.update_status(
        item_id=item_id,
        new_status=data.status,
        user=user,
    )