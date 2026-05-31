from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order_item import OrderItem, OrderItemStatus
from app.models.user import User, UserRole
from app.models.order import OrderStatus

from app.domain.order.order_service import OrderService
from app.domain.order_item.order_item_transitions import can_transition
from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.services.event_service import EventService



class OrderItemService:

    def __init__(self, db: Session):
        self.db = db
        self.events = EventService(db)

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
            raise DomainError(
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

        order = item.order
        order_service = OrderService(self.db)

        previous_status = self.change_item_status(
            item,
            new_status,
            user,
            order_service
        )

        # =========================
        # EVENTOS
        # =========================

        payload = {
            "order_id": order.id,
            "item_id": item.id,
            "status": new_status.value,
            "product": item.product.name,
            "quantity": item.quantity,
            "table": order.table.number
        }

        # cocina
        self.events.emit(
            restaurant_id=order.restaurant_id,
            event_type="ITEM_STATUS_CHANGED",
            payload=payload,
            target="station",
            target_id=str(item.product.station_id)
        )

        # salón / administración
        for role in [UserRole.ADMIN, UserRole.WAITER]:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type="ITEM_STATUS_CHANGED",
                payload=payload,
                target="role",
                target_id=role.value
            )

        # evento READY
        if new_status == OrderItemStatus.READY:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type="ITEM_READY",
                payload={
                    "order_id": order.id,
                    "table": order.table.number,
                    "product": item.product.name,
                    "quantity": item.quantity
                },
                target="role",
                target_id=UserRole.WAITER.value
            )

        # cambio estado orden
        if order.status != previous_status:
            for role in [UserRole.ADMIN, UserRole.WAITER]:
                self.events.emit(
                    restaurant_id=order.restaurant_id,
                    event_type="ORDER_STATUS_CHANGED",
                    payload={
                        "order_id": order.id,
                        "status": order.status.value
                    },
                    target="role",
                    target_id=role.value
                )
        self.db.commit()
        self.db.refresh(item)
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
            raise DomainError(
                "No se pueden modificar items en una orden cerrada",
                ErrorCode.ORDER_ALREADY_CLOSED,
                context={"order_id": order.id}
            )

        # reglas por rol
        if new_status == OrderItemStatus.IN_PROGRESS and user.role != UserRole.KITCHEN:
            raise DomainError(
                "Sólo COCINA puede comenzar items",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={"required_role": "KITCHEN"}
            )

        if new_status == OrderItemStatus.READY and user.role != UserRole.KITCHEN:
            raise DomainError(
                "Sólo COCINA puede marcar items como listos",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={"required_role": "KITCHEN"}
            )

        if new_status == OrderItemStatus.DELIVERED and user.role != UserRole.WAITER:
            raise DomainError(
                "Sólo MOZO puede entregar items",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={"required_role": "WAITER"}
            )

        if not can_transition(item.status, new_status):
            raise DomainError(
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
