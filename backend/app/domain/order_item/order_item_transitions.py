from app.models.order_item import OrderItemStatus


_ALLOWED_TRANSITIONS = {
    OrderItemStatus.PENDING: [
        OrderItemStatus.SENT,
        OrderItemStatus.CANCELLED
    ],
    OrderItemStatus.SENT: [
        OrderItemStatus.IN_PROGRESS,
        OrderItemStatus.CANCELLED
    ],
    OrderItemStatus.IN_PROGRESS: [
        OrderItemStatus.READY,
        OrderItemStatus.CANCELLED
    ],
    OrderItemStatus.READY: [
        OrderItemStatus.DELIVERED
    ],
    OrderItemStatus.DELIVERED: [],
    OrderItemStatus.CANCELLED: []
}


def can_transition(current: OrderItemStatus, new: OrderItemStatus) -> bool:
    return new in _ALLOWED_TRANSITIONS.get(current, [])


def allowed_transitions(status: OrderItemStatus) -> list[OrderItemStatus]:
    return _ALLOWED_TRANSITIONS.get(status, [])