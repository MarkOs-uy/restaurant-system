from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.dependencies.auth import get_current_user

from app.schemas.order.order_item import OrderItemStatusUpdate

from app.domain.order_item.order_item_service import OrderItemService

router = APIRouter(
    prefix="/order-items",
    tags=["order-items"]
)

@router.patch("/{item_id}/status")
async def update_item_status(
    item_id: int,
    data: OrderItemStatusUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    service = OrderItemService(db)

    item = service.update_status(
        item_id=item_id,
        new_status=data.status,
        user=user
    )

    return {
        "item_id": item.id,
        "new_status": item.status
    }