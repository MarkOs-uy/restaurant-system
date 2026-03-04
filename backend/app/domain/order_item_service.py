from app.models.order_item import OrderItem, OrderItemStatus
from app.models.user import User, UserRole
from app.models.order import OrderStatus
from app.domain.order_item_transitions import can_transition


class OrderItemDomainError(Exception):
    pass


def change_item_status(item: OrderItem, new_status: OrderItemStatus, user: User):

    if item.order.status == OrderStatus.CLOSED:
        raise OrderItemDomainError("Cannot modify items of closed order")

    # 🔐 reglas por rol
    if new_status == OrderItemStatus.IN_PROGRESS and user.role != UserRole.KITCHEN:
        raise OrderItemDomainError("Only kitchen can start items")

    if new_status == OrderItemStatus.READY and user.role != UserRole.KITCHEN:
        raise OrderItemDomainError("Only kitchen can mark ready")

    if new_status == OrderItemStatus.DELIVERED and user.role != UserRole.WAITER:
        raise OrderItemDomainError("Only waiter can deliver")

    if not can_transition(item.status, new_status):
        raise OrderItemDomainError(
            f"Invalid transition from {item.status.value} to {new_status.value}"
        )

    item.status = new_status