import logging

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.domain.order.order_service import OrderService
from app.domain.order_item.order_item_transitions import can_transition
from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode
from app.domain.events.websocket import WSEvent

from app.services.event_service import EventService

from app.utils.money import money

from app.models.order_item import OrderItem, OrderItemStatus
from app.models.user import User, UserRole
from app.models.order import OrderStatus

from app.schemas.order.order import OrderResponse

logger = logging.getLogger("app.domain.order_item")

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

        if order.status == OrderStatus.CANCELLED:
            raise DomainError(
                "No se pueden modificar items en una orden cancelada",
                ErrorCode.ORDER_ALREADY_CANCELLED,
                context={"order_id": order.id}
            )

        if (
            new_status == OrderItemStatus.IN_PROGRESS
            and user.role != UserRole.KITCHEN
        ):
            raise DomainError(
                "Sólo COCINA puede comenzar items",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={"required_role": "KITCHEN"}
            )

        if (
            new_status == OrderItemStatus.READY
            and user.role != UserRole.KITCHEN
        ):
            raise DomainError(
                "Sólo COCINA puede marcar items como listos",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={"required_role": "KITCHEN"}
            )

        if (
            new_status == OrderItemStatus.DELIVERED
            and user.role != UserRole.WAITER
        ):
            raise DomainError(
                "Sólo MOZO puede entregar items",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={"required_role": "WAITER"}
            )

        if (
            new_status == OrderItemStatus.CANCELLED
            and user.role not in (
                UserRole.WAITER,
                UserRole.ADMIN
            )
        ):
            raise DomainError(
                "Sólo MOZO o ADMIN puede cancelar items",
                ErrorCode.ITEM_STATUS_ROLE_FORBIDDEN,
                context={
                    "required_roles": [
                        UserRole.WAITER.value,
                        UserRole.ADMIN.value
                    ]
                }
            )

        if not can_transition(
            item.status,
            new_status
        ):
            raise DomainError(
                (
                    f"Transición inválida desde "
                    f"{item.status.value} a {new_status.value}"
                ),
                ErrorCode.ITEM_INVALID_TRANSITION,
                context={
                    "from": item.status.value,
                    "to": new_status.value
                }
            )
        item.status = new_status
        previous_status = order.status
        new_order_status = (order_service._calculate_order_status(order))
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

        if new_status == OrderItemStatus.CANCELLED:
            raise DomainError(
                "La cancelación de items debe realizarse mediante la operación específica de cancelación",
                ErrorCode.INVALID_OPERATION
            )

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

    # -------------------------
    # Cancelar item
    # -------------------------
    def cancel_item(
        self,
        item_id: int,
        reason: str,
        user: User
    ) -> OrderResponse:

        item = self._get_item(
            item_id,
            user.restaurant_id
        )

        order = item.order

        reason = reason.strip()

        if not reason:
            raise DomainError(
                "Debe indicar un motivo para cancelar el item",
                ErrorCode.INVALID_OPERATION,
                context={"item_id": item.id}
            )

        # --------------------------------------------------
        # La tabla de transiciones sigue siendo la fuente
        # de verdad respecto a qué estados pueden cancelarse.
        #
        # PENDING no admite CANCELLED: debe eliminarse.
        # DELIVERED y CANCELLED son estados finales.
        # --------------------------------------------------
        if not can_transition(
            item.status,
            OrderItemStatus.CANCELLED
        ):
            raise DomainError(
                (
                    f"No se puede cancelar un item "
                    f"en estado {item.status.value}"
                ),
                ErrorCode.ITEM_INVALID_TRANSITION,
                context={
                    "item_id": item.id,
                    "from": item.status.value,
                    "to": OrderItemStatus.CANCELLED.value
                }
            )

        order_service = OrderService(self.db)

        # --------------------------------------------------
        # Validación financiera
        #
        # Cancelar el item reduce el subtotal y, por tanto,
        # puede dejar inválido un descuento existente o hacer
        # que lo ya pagado supere el nuevo total.
        # --------------------------------------------------
        subtotal, _, total_paid, _ = (
            order_service._calculate_totals(order)
        )

        item_amount = (
            item.quantity * item.unit_price
        )

        new_subtotal = (
            subtotal - item_amount
        )

        discount = (
            order.discount or Decimal("0")
        )

        if discount > new_subtotal:
            raise DomainError(
                (
                    "No se puede cancelar el item porque "
                    "el descuento de la orden superaría "
                    "el nuevo subtotal"
                ),
                ErrorCode.INVALID_OPERATION,
                context={
                    "item_id": item.id,
                    "new_subtotal": money(new_subtotal),
                    "discount": money(discount)
                }
            )

        new_total = max(
            new_subtotal - discount,
            Decimal("0")
        )

        if total_paid > new_total:
            raise DomainError(
                (
                    "No se puede cancelar el item porque "
                    "el monto pagado superaría el nuevo total"
                ),
                ErrorCode.INVALID_OPERATION,
                context={
                    "item_id": item.id,
                    "new_total": money(new_total),
                    "total_paid": money(total_paid)
                }
            )

        # --------------------------------------------------
        # Transición de estado.
        #
        # Acá se validan también:
        # - estado de la orden
        # - rol del usuario
        # - transición del item
        # - nuevo estado general de la orden
        # --------------------------------------------------
        previous_order_status = (
            self._process_status_transition(
                item=item,
                new_status=OrderItemStatus.CANCELLED,
                user=user,
                order_service=order_service
            )
        )

        # --------------------------------------------------
        # Auditoría del item
        # --------------------------------------------------
        cancelled_at = datetime.now(
            timezone.utc
        )

        item.cancelled_at = cancelled_at
        item.cancelled_by_id = user.id
        item.cancellation_reason = reason

        # --------------------------------------------------
        # Si era el último item activo,
        # _calculate_order_status() habrá cancelado también
        # la orden. Registramos su auditoría.
        # --------------------------------------------------
        if (
            previous_order_status != OrderStatus.CANCELLED
            and order.status == OrderStatus.CANCELLED
        ):
            order.cancelled_at = cancelled_at
            order.cancelled_by_id = user.id
            order.cancellation_reason = reason

        logger.info(
            (
                "Item cancelado "
                "order_id=%s item_id=%s "
                "user_id=%s reason=%s"
            ),
            order.id,
            item.id,
            user.id,
            reason
        )

        # ==================================================
        # EVENTOS
        # ==================================================

        payload = {
            "order_id": order.id,
            "item_id": item.id,
            "status": item.status.value,
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
        # Salón / administración / caja
        #
        # Caja también debe enterarse porque la cancelación
        # modifica subtotal, total y saldo de la orden.
        # --------------------------------------------------
        for role in [
            UserRole.ADMIN,
            UserRole.WAITER,
            UserRole.CASHIER
        ]:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type=WSEvent.ITEM_STATUS_CHANGED,
                payload=payload,
                target="role",
                target_id=role.value
            )

            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type=WSEvent.ORDER_UPDATED,
                payload={
                    "order_id": order.id
                },
                target="role",
                target_id=role.value
            )

        # --------------------------------------------------
        # Si cambió también el estado general de la orden.
        #
        # Por ejemplo:
        # READY → CANCELLED
        # al cancelar el último item activo.
        # --------------------------------------------------
        if order.status != previous_order_status:
            for role in [
                UserRole.ADMIN,
                UserRole.WAITER,
                UserRole.CASHIER
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
        # Un único commit:
        #
        # - cancelación del item
        # - posible cancelación de la orden
        # - auditoría
        # - eventos Outbox
        #
        # todo queda dentro de la misma transacción.
        # --------------------------------------------------
        self.db.commit()

        self.db.refresh(item)
        self.db.refresh(order)

        return order_service.to_order_response(
            order
        )