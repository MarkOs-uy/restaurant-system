# app/domain/order_transitions.py

from app.models.order import OrderStatus

ORDER_ALLOWED_TRANSITIONS = {
    OrderStatus.OPEN: [
        OrderStatus.SENT,
        OrderStatus.CANCELLED
    ],
    OrderStatus.SENT: [
        OrderStatus.IN_PROGRESS,
        OrderStatus.CANCELLED
    ],
    OrderStatus.IN_PROGRESS: [
        OrderStatus.READY,
        OrderStatus.CANCELLED
    ],
    OrderStatus.READY: [
        OrderStatus.CLOSED
    ],
    OrderStatus.CLOSED: [],
    OrderStatus.CANCELLED: []
}


def is_valid_order_transition(
    current_status: OrderStatus,
    new_status: OrderStatus
) -> bool:
    """
    Valida si una transición de estado de orden es permitida.
    """

    allowed = ORDER_ALLOWED_TRANSITIONS.get(current_status, [])

    return new_status in allowed