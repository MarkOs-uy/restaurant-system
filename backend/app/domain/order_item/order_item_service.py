from sqlalchemy.orm import Session

from app.domain.order.order_service import OrderService
from app.domain.order_item.order_item_transitions import can_transition
from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode
from app.domain.events.websocket import WSEvent

from app.services.event_service import EventService

from app.models.order_item import OrderItem, OrderItemStatus
from app.models.user import User, UserRole
from app.models.order import OrderStatus

class OrderItemService:

    """
    Servicio encargado de la lógica de negocio relacionada con los items de las ordenes.

    Responsabilidades:
    - Gestionar el ciclo de vida de las items.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventService(db)

    # -------------------------
    # Obtener item
    # -------------------------
    def _get_item(self, item_id: int, restaurant_id: int) -> OrderItem:
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
                context={"item_id": item_id})
        return item

    # -----------------------------------------------------------------------------
    # Procesar transición de estado del item y recalcular estado de la orden
    # -----------------------------------------------------------------------------
    def _process_status_transition(
        self,
        item: OrderItem,
        new_status: OrderItemStatus,
        user: User,
        order_service: OrderService
    ) -> OrderStatus:
        order = item.order
        if order.status == OrderStatus.CLOSED:
            raise DomainError(
                "No se pueden modificar items en una orden cerrada",
                ErrorCode.ORDER_ALREADY_CLOSED,
                context={"order_id": order.id}
            )
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
        new_order_status = order_service._calculate_order_status(order)
        order_service._set_status(order, new_order_status)
        return previous_status

    # -------------------------
    # Actualizar estado
    # -------------------------
    def update_status(
        self,
        item_id: int,
        new_status: OrderItemStatus,
        user: User
    ) -> OrderItem:

        item = self._get_item(
            item_id,
            user.restaurant_id
        )

        order = item.order

        order_service = OrderService(
            self.db
        )

        previous_status = (
            self._process_status_transition(
                item,
                new_status,
                user,
                order_service
            )
        )

        # ==================================================
        # EVENTOS
        # ==================================================

        payload = {
            "order_id": order.id,
            "item_id": item.id,
            "status": new_status.value,
            "product": item.product.name,
            "quantity": item.quantity,
            "table": order.table.number
        }

        # --------------------------------------------------
        # Cocina
        # --------------------------------------------------
        self.events.emit(
            restaurant_id=order.restaurant_id,
            event_type=WSEvent.ITEM_STATUS_CHANGED,
            payload=payload,
            target="station",
            target_id=str(
                item.product.station_id
            )
        )

        # --------------------------------------------------
        # Salón / administración
        # --------------------------------------------------
        for role in [
            UserRole.ADMIN,
            UserRole.WAITER
        ]:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type=WSEvent.ITEM_STATUS_CHANGED,
                payload=payload,
                target="role",
                target_id=role.value
            )

        # --------------------------------------------------
        # Ítem listo
        # --------------------------------------------------
        if new_status == OrderItemStatus.READY:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type=WSEvent.ITEM_READY,
                payload={
                    "order_id": order.id,
                    "table": order.table.number,
                    "product": item.product.name,
                    "quantity": item.quantity
                },
                target="role",
                target_id=UserRole.WAITER.value
            )

        # --------------------------------------------------
        # Cambio de estado general de la orden
        # --------------------------------------------------
        if order.status != previous_status:
            for role in [
                UserRole.ADMIN,
                UserRole.WAITER
            ]:
                self.events.emit(
                    restaurant_id=order.restaurant_id,
                    event_type=WSEvent.ORDER_STATUS_CHANGED,
                    payload={
                        "order_id": order.id,
                        "status": order.status.value
                    },
                    target="role",
                    target_id=role.value
                )

        # --------------------------------------------------
        # Commit atómico:
        #
        # cambio del dominio + eventos Outbox.
        # --------------------------------------------------
        self.db.commit()
        self.db.refresh(item)

        return item