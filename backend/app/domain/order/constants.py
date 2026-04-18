from app.models.order import OrderStatus

ACTIVE_ORDER_STATUSES = [
    OrderStatus.DRAFT,
    OrderStatus.OPEN,
    OrderStatus.SENT,
    OrderStatus.IN_PROGRESS,
    OrderStatus.READY
]