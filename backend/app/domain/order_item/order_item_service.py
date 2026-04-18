from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order_item import OrderItem, OrderItemStatus
from app.models.user import User, UserRole
from app.models.order import OrderStatus

from app.domain.order.order_service import OrderService
from app.domain.order_item.order_item_transitions import can_transition
from app.domain.errors import OrderItemDomainError
from app.domain.error_codes import ErrorCode

from app.services.event_service import event_service



class OrderItemService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Obtener item
    # -------------------------
    
    def get_item(self, item_id: int, restaurant_id: int):

        item = (
            self.db.query(OrderItem)
            .filter(
                OrderItem.id == item_id,
                OrderItem.restaurant_id == restaurant_id
            )
            .first()
        )

        if not item:
            raise OrderItemDomainError(
                "Item no encontrado",
                ErrorCode.ITEM_NOT_FOUND,
                context={"Item:": item_id })

        return item

    # -------------------------
    # Actualizar estado
    # -------------------------

    def update_status(
        self,
        item_id: int,
        new_status: OrderItemStatus,
        user: User
    ):

        item = self.get_item(item_id, user.restaurant_id)

        order_service = OrderService(self.db)

        previous_status = self.change_item_status(
            item,
            new_status,
            user,
            order_service
        )

        self.db.commit()
        self.db.refresh(item)

        order = item.order

        # =========================
        # EVENTOS
        # =========================

        payload = {
            "type": "ITEM_STATUS_CHANGED",
            "order_id": order.id,
            "item_id": item.id,
            "status": new_status.value,
            "product": item.product.name,
            "quantity": item.quantity,
            "table": order.table.number
        }

        # cocina
        event_service.emit_to_station(
            order.restaurant_id,
            item.product.station_id,
            payload
        )

        # mozos
        event_service.emit_to_role(
            order.restaurant_id,
            UserRole.WAITER,
            payload
        )

        # evento especial READY
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

        # cambio de estado de orden
        if order.status != previous_status:

            event_service.emit_to_role(
                order.restaurant_id,
                UserRole.WAITER,
                {
                    "type": "ORDER_STATUS_CHANGED",
                    "order_id": order.id,
                    "status": order.status.value
                }
            )

        return item
    
    # -------------------------
    # Cambiar estado
    # -------------------------

    def change_item_status(
        self,
        item: OrderItem,
        new_status: OrderItemStatus,
        user: User,
        order_service: OrderService
    ):

        order = item.order

        if order.status == OrderStatus.CLOSED:
            raise OrderItemDomainError(
                "No se pueden modificar items en una orden cerrada",
                ErrorCode.ORDER_ALREADY_CLOSED,
                context={"order_id": order.id}
            )

        # reglas por rol

        if new_status == OrderItemStatus.IN_PROGRESS and user.role != UserRole.KITCHEN:
            raise OrderItemDomainError(
                "Sólo COCINA puede comenzar items",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={"required_role": "KITCHEN"}
            )

        if new_status == OrderItemStatus.READY and user.role != UserRole.KITCHEN:
            raise OrderItemDomainError(
                "Sólo COCINA puede marcar items como listos",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={"required_role": "KITCHEN"}
            )

        if new_status == OrderItemStatus.DELIVERED and user.role != UserRole.WAITER:
            raise OrderItemDomainError(
                "Sólo MOZO puede entregar items",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={"required_role": "WAITER"}
            )

        if not can_transition(item.status, new_status):
            raise OrderItemDomainError(
                f"Transición inválida desde {item.status.value} a {new_status.value}",
                ErrorCode.ITEM_INVALID_TRANSITION,
                context={
                    "from": item.status.value,
                    "to": new_status.value
                }
            )

        item.status = new_status

        previous_status = order.status

        order_service.recalculate_order_status(order)

        return previous_status
