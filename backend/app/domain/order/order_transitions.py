# app/domain/order_transitions.py

from app.models.order import OrderStatus

ORDER_ALLOWED_TRANSITIONS = {
    OrderStatus.DRAFT: [
        OrderStatus.OPEN,
        OrderStatus.CANCELLED
    ],
    OrderStatus.OPEN: [
        OrderStatus.SENT,
        OrderStatus.CANCELLED
    ],
    OrderStatus.SENT: [
        OrderStatus.IN_PROGRESS,
        OrderStatus.READY,
        OrderStatus.CANCELLED
    ],
    OrderStatus.IN_PROGRESS: [
        OrderStatus.SENT,
        OrderStatus.READY,
        OrderStatus.CANCELLED
    ],
    OrderStatus.READY: [
        OrderStatus.OPEN,
        OrderStatus.SENT,
        OrderStatus.CLOSED
    ],
    OrderStatus.CLOSED: [],
    OrderStatus.CANCELLED: []
}


def is_valid_order_transition(
    current_status: OrderStatus,
    new_status: OrderStatus
) -> bool:
    allowed = ORDER_ALLOWED_TRANSITIONS.get(current_status, [])
    return new_status in allowed