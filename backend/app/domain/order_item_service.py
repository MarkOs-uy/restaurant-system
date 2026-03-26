from app.models.order_item import OrderItem, OrderItemStatus
from app.models.user import User, UserRole
from app.models.order import OrderStatus
from app.domain.order_item_transitions import can_transition
from app.domain.order_service import OrderService
from app.domain.event_service import event_service
from app.websocket.manager import manager

class OrderItemDomainError(Exception):
    pass


def change_item_status(
    item: OrderItem,
    new_status: OrderItemStatus,
    user: User,
    order_service: OrderService
):

    order = item.order

    if order.status == OrderStatus.CLOSED:
        raise OrderItemDomainError("No se pueden modificar items en una orden cerrada")

    # 🔐 reglas por rol
    if new_status == OrderItemStatus.IN_PROGRESS and user.role != UserRole.KITCHEN:
        raise OrderItemDomainError("Sólo COCINA COMIENZA items")

    if new_status == OrderItemStatus.READY and user.role != UserRole.KITCHEN:
        raise OrderItemDomainError("Sólo COCINA marca como LISTO")

    if new_status == OrderItemStatus.DELIVERED and user.role != UserRole.WAITER:
        raise OrderItemDomainError("Sólo MOZO puede ENTREGAR")

    if not can_transition(item.status, new_status):
        raise OrderItemDomainError(
            f"Transición inválida desde {item.status.value} a {new_status.value}"
        )

    # 🔄 cambiar estado del item
    item.status = new_status

    # 🔥 recalcular orden
    previous_status = order.status
    order_service.recalculate_order_status(order)

    # =========================
    # 🔔 EVENTOS
    # =========================

    if order.status != previous_status:

        # 👉 cocina (solo la estación afectada)
        event_service.emit_to_station(
            order.restaurant_id,
            item.product.station_id,
            {
                "type": "ITEM_STATUS_CHANGED",
                "order_id": order.id,
                "item_id": item.id,
                "status": new_status.value
            }
        )

        # 👉 si es READY
        if new_status == OrderItemStatus.READY:
            event_service.emit_to_role(
                order.restaurant_id,
                UserRole.WAITER,
                {
                    "type": "ITEM_READY",
                    "order_id": order.id,
                    "table": order.table.number,
                    "product": item.product.name,
                    "quantity": item.quantity
                }
            )