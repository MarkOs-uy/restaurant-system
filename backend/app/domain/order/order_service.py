import logging

from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.domain.order.order_transitions import is_valid_order_transition
from app.domain.order.constants import ACTIVE_ORDER_STATUSES
from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.services.event_service import EventService

from app.utils.money import money

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product
from app.models.user import UserRole
from app.models.payment import Payment
from app.models.table import Table

from app.schemas.order.order import OrderResponse
from app.schemas.order.order_item import (
    OrderItemCreate,
    OrderItemOut
)
from app.schemas.order.payment import (
    PaymentCreate,
    PaymentOut
)

logger = logging.getLogger("app.domain.order")

class OrderService:

    """
    Servicio encargado de la lógica de negocio relacionada con las ordenes.

    Responsabilidades:
    - Gestionar el ciclo de vida de las órdenes.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventService(db)

    # -------------------------
    # Obtener ordenes activas
    # -------------------------
    def _get_active_orders(self, restaurant_id: int) -> list[Order]:
        return (
            self.db.query(Order)
            .options(
                joinedload(Order.items).joinedload(OrderItem.product),
                joinedload(Order.payments),
                joinedload(Order.table)
            )
            .filter(Order.restaurant_id == restaurant_id,
                    Order.status.in_(ACTIVE_ORDER_STATUSES))
            .all()
        )

    # -------------------------
    # Obtener orden activa por mesa
    # -------------------------
    def _get_active_order(self, restaurant_id: int, table_id: int) -> Order:
        return (
            self.db.query(Order)
            .filter(
                Order.restaurant_id == restaurant_id,
                Order.table_id == table_id,
                Order.status.in_(ACTIVE_ORDER_STATUSES)
            )
            .first()
        )

    # -------------------------
    # Calcular totales de la orden
    # -------------------------
    def _calculate_totals(self, order: Order) -> tuple[Decimal, Decimal, Decimal, Decimal]:
        subtotal = sum((item.quantity * item.unit_price for item in order.items), Decimal("0"))
        discount = order.discount or Decimal("0")
        total = max(subtotal - discount, Decimal("0"))
        total_paid = sum(payment.amount for payment in order.payments)
        remaining = total - total_paid
        return subtotal, total, total_paid, remaining

    # -------------------------
    # Calcular estado de la orden basado en estados de los items
    # -------------------------
    def _calculate_order_status(self, order: Order) -> OrderStatus:
        active_items = [
            i for i in order.items
            if i.status != OrderItemStatus.CANCELLED
        ]
        if not active_items:
            if order.status in (OrderStatus.DRAFT, OrderStatus.OPEN):
                return OrderStatus.CANCELLED
            return order.status
        statuses = [i.status for i in active_items]
        if any(s == OrderItemStatus.IN_PROGRESS for s in statuses):
            return OrderStatus.IN_PROGRESS
        if any(s == OrderItemStatus.SENT for s in statuses):
            return OrderStatus.SENT
        if any(s == OrderItemStatus.PENDING for s in statuses):
            return OrderStatus.OPEN
        if all(
            s in (OrderItemStatus.READY, OrderItemStatus.DELIVERED)
            for s in statuses
        ):
            return OrderStatus.READY
        return order.status

    # -------------------------
    # Cambiar estado de la orden si es diferente al actual
    # -------------------------
    def _set_status(self, order: Order, new_status: OrderStatus) -> bool:
        if order.status == new_status:
            return False
        if not is_valid_order_transition(order.status, new_status):
            raise DomainError(
                "Invalid order status transition",
                ErrorCode.INVALID_TRANSITION,
                context={
                    "from": order.status.value,
                    "to": new_status.value,
                    "order_id": order.id
                }
            )
        order.status = new_status
        return True

    # -------------------------
    # Obtener orden por id
    # -------------------------
    def get_order(self, order_id: int, restaurant_id: int) -> Order:
        order = (
            self.db.query(Order)
            .options(
                joinedload(Order.items).joinedload(OrderItem.product),
                joinedload(Order.payments),
                joinedload(Order.table)
            )
            .filter(Order.id == order_id, Order.restaurant_id == restaurant_id)
            .first()
        )
        if not order:
            raise DomainError(
                "Orden no encontrada",
                ErrorCode.ORDER_NOT_FOUND
            )
        return order

    # -------------------------------------------------------------------------------------------------
    # Devolver orden con items, pagos, subtotal, descuento, totales y remanentes
    # -------------------------------------------------------------------------------------------------
    def to_order_response(
        self,
        order: Order
    ) -> OrderResponse:
        subtotal, total, total_paid, remaining = self._calculate_totals(order)
        return OrderResponse(
            id=order.id,
            table_id=order.table_id,
            table_number=order.table.number,
            status=order.status,
            created_at=order.created_at,
            items=[
                OrderItemOut(
                    id=item.id,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    unit_price=money(item.unit_price),
                    subtotal=money(item.quantity * item.unit_price),
                    status=item.status
                )
                for item in order.items
            ],
            payments=[
                PaymentOut(
                    id=payment.id,
                    amount=money(payment.amount),
                    method=payment.method
                )
                for payment in order.payments
            ],
            subtotal=money(subtotal),
            discount=money(order.discount or 0),
            total=money(total),
            total_paid=money(total_paid),
            remaining=money(remaining)
        )

    # -------------------------------------------------------------------------------------------------
    # Devolver lista de órdenes activas con items, pagos, subtotal, descuento, totales y remanentes
    # -------------------------------------------------------------------------------------------------
    def to_order_response_list(
        self,
        restaurant_id: int
    ) -> list[OrderResponse]:
        orders = self._get_active_orders(restaurant_id)
        return [
            self.to_order_response(order)
            for order in orders
        ]

    # -------------------------
    # Aplicar descuento a la orden
    # -------------------------
    def apply_discount(self, order: Order, discount: Decimal) -> OrderResponse:
        if order.status == OrderStatus.CLOSED:
            raise DomainError(
                "Cannot apply discount to closed order",
                ErrorCode.ORDER_ALREADY_CLOSED
            )
        if order.status == OrderStatus.CANCELLED:
            raise DomainError(
                "Cannot apply discount to cancelled order",
                ErrorCode.INVALID_OPERATION
            )
        discount = discount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        subtotal, _, total_paid, _ = self._calculate_totals(order)
        if discount > subtotal:
            raise DomainError(
                "Discount cannot exceed order subtotal",
                ErrorCode.INVALID_OPERATION,
                context={
                    "discount": money(discount),
                    "subtotal": money(subtotal)
                }
            )
        new_total = subtotal - discount
        if new_total < total_paid:
            raise DomainError(
                "Discount would make paid amount exceed order total",
                ErrorCode.INVALID_OPERATION,
                context={
                    "discount": money(discount),
                    "new_total": money(new_total),
                    "total_paid": money(total_paid)
                }
            )
        logger.info("Descuento aplicado order_id=%s discount=%s", order.id, discount)
        order.discount = discount
        for role in [UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER]:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type="ORDER_UPDATED",
                payload={"order_id": order.id},
                target="role",
                target_id=role.value
            )
        self.db.commit()
        self.db.refresh(order)
        return self.to_order_response(order)

    # -------------------------
    # Crear / agregar items
    # -------------------------
    def add_item(self, order: Order, data: OrderItemCreate) -> OrderResponse:
        if order.status == OrderStatus.CLOSED:
            raise DomainError(
                "Cannot add items to closed order",
                ErrorCode.ORDER_ALREADY_CLOSED
            )
        if data.quantity <= 0:
            raise DomainError(
                "Quantity must be greater than zero",
                ErrorCode.INVALID_OPERATION
            )
        product = (
            self.db.query(Product)
            .filter(
                Product.id == data.product_id,
                Product.restaurant_id == order.restaurant_id,
                Product.active
            )
            .first()
        )
        if not product:
            raise DomainError(
                "Product not found",
                ErrorCode.ITEM_NOT_FOUND,
                context={"product_id": data.product_id}
            )
        
        previous_status = order.status

        existing_item = (
            self.db.query(OrderItem)
            .filter(
                OrderItem.order_id == order.id,
                OrderItem.product_id == product.id,
                OrderItem.status == OrderItemStatus.PENDING
            )
            .first()
        )
        if existing_item:
            existing_item.quantity += data.quantity
            item = existing_item
        else:
            item = OrderItem(
                restaurant_id=order.restaurant_id,
                order_id=order.id,
                product_id=product.id,
                quantity=data.quantity,
                unit_price=product.price,
                status=OrderItemStatus.PENDING
            )
            self.db.add(item)        
        self.db.flush()
        new_status = self._calculate_order_status(order)
        self._set_status(order, new_status)
        self.db.commit()
        self.db.refresh(order)
        # =========================
        # 🔔 EVENTOS
        # =========================
        self.events.emit(
            restaurant_id=order.restaurant_id,
            event_type="NEW_ITEM",
            payload={"order_id": order.id},
            target="station",
            target_id=str(product.station_id)
        )
        if order.status != previous_status:
            for role in [UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER]:
                self.events.emit(
                    restaurant_id=order.restaurant_id,
                    event_type="ORDER_STATUS_CHANGED",
                    payload={"order_id": order.id, "status": order.status.value},
                    target="role",
                    target_id=role.value
                )
        for role in [UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER]:
            logger.debug("ORDER_UPDATED emit order_id=%s", order.id)
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type="ORDER_UPDATED",
                payload={"order_id": order.id},
                target="role",
                target_id=role.value
            )
        return self.to_order_response(order)

    # -------------------------
    # Agregar producto a la mesa (crear orden si no existe)
    # -------------------------
    def add_product_to_order(self, restaurant_id: int, table_id: int, data: OrderItemCreate):
        table = self.db.query(Table).filter(Table.id == table_id, Table.restaurant_id == restaurant_id).first()
        if not table:
            raise DomainError(
                "Table not found",
                ErrorCode.TABLE_NOT_FOUND
            )
        order = self._get_active_order(restaurant_id, table_id)
        if not order:
            order = Order(table_id=table_id, restaurant_id=restaurant_id, status=OrderStatus.OPEN)
            self.db.add(order)
            self.db.flush()
        item = self.add_item(order, data)
        return {"order_id": order.id, "item_id": item.id}

    # -------------------------
    # Actualizar estado de la orden
    # -------------------------
    def update_status(self, order: Order, new_status: OrderStatus) -> OrderResponse:
        if order.status == new_status:
            return self.to_order_response(order)
        previous_status = order.status
        if self._set_status(order, new_status):
            logger.info(
                "Estado de orden actualizado order_id=%s from=%s to=%s",
                order.id, previous_status.value, new_status.value
            )
            self.db.commit()
            self.db.refresh(order)
            for role in [UserRole.ADMIN, UserRole.WAITER]:
                self.events.emit(
                    restaurant_id=order.restaurant_id,
                    event_type="ORDER_STATUS_CHANGED",
                    payload={"order_id": order.id, "status": new_status.value},
                    target="role",
                    target_id=role.value
                )
        return self.to_order_response(order)

    # -------------------------
    # Enviar a cocina
    # -------------------------
    def send_to_kitchen(self, order: Order) -> OrderResponse:
        if order.status == OrderStatus.CLOSED:
            raise DomainError(
                "Order is closed",
                ErrorCode.ORDER_ALREADY_CLOSED
            )
        pending_items = [i for i in order.items if i.status == OrderItemStatus.PENDING]
        if not pending_items:
            raise DomainError(
                "No pending items to send",
                ErrorCode.NO_PENDING_ITEMS_TO_SEND
            )
        previous_status = order.status
        for item in pending_items:
            item.status = OrderItemStatus.SENT
        logger.info("Orden enviada a cocina order_id=%s r=%s", order.id, order.restaurant_id)
        new_status = self._calculate_order_status(order)
        self._set_status(order, new_status)
        self.db.commit()
        self.db.refresh(order)
        station_ids = {i.product.station_id for i in pending_items}
        for station_id in station_ids:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type="ORDER_UPDATED",
                payload={"order_id": order.id},
                target="station",
                target_id=str(station_id)
            )
        if order.status != previous_status:
            for role in [UserRole.ADMIN, UserRole.WAITER]:
                self.events.emit(
                    restaurant_id=order.restaurant_id,
                    event_type="ORDER_STATUS_CHANGED",
                    payload={"order_id": order.id, "status": order.status.value},
                    target="role",
                    target_id=role.value
                )
        return self.to_order_response(order)

    # -------------------------
    # Agregar pago
    # -------------------------
    def add_payment(self, order: Order, data: PaymentCreate) -> Payment:
        from app.domain.cash_register.cash_register_service import CashRegisterService
        if order.status == OrderStatus.CLOSED:
            raise DomainError(
                "Order already closed",
                ErrorCode.ORDER_ALREADY_CLOSED
            )
        cash_service = CashRegisterService(self.db)
        cash_register = cash_service.get_open_cash_register(order.restaurant_id)
        subtotal, total, total_paid, remaining = self._calculate_totals(order)
        if data.amount > remaining:
            raise DomainError(
                "Payment exceeds remaining balance",
                ErrorCode.PAYMENT_EXCEEDS_REMAINING,
                context={
                    "amount": money(data.amount),
                    "remaining": money(remaining)
                }
            )
        logger.info("Pago agregado order_id=%s amount=%s method=%s", order.id, data.amount, data.method)
        payment = Payment(
            order_id=order.id,
            restaurant_id=order.restaurant_id,
            amount=data.amount,
            method=data.method,
            cash_register_id=cash_register.id
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        for role in [UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER]:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type="PAYMENT_ADDED",
                payload={"order_id": order.id, "amount": money(data.amount), "method": data.method},
                target="role",
                target_id=role.value
            )
        self.events.emit(
            restaurant_id=order.restaurant_id,
            event_type="CASH_REGISTER_UPDATED",
            payload={"order_id": order.id},
            target="role",
            target_id=UserRole.CASHIER.value
        )
        return payment

    # -------------------------
    # Borrar pago
    # -------------------------
    def delete_payment(self, restaurant_id: int, payment_id: int):
        payment = (
            self.db.query(Payment)
            .filter(
                Payment.id == payment_id,
                Payment.restaurant_id == restaurant_id
            )
            .first()
        )

        if not payment:
            raise DomainError(
                "Pago no encontrado",
                ErrorCode.PAYMENT_NOT_FOUND
                )

        if payment.order.status == OrderStatus.CLOSED:
            raise DomainError(
                "Cannot delete payment from closed order",
                ErrorCode.INVALID_OPERATION
            )
        logger.info("Pago eliminado order_id=%s amount=%s method=%s", payment.order_id, payment.amount, payment.method)
        order_id = payment.order_id
        amount = payment.amount
        method = payment.method

        self.db.delete(payment)
        self.db.commit()
        for role in [UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER]:
            self.events.emit(
                restaurant_id=restaurant_id,
                event_type="PAYMENT_DELETED",
                payload={
                    "order_id": order_id,
                    "amount": money(amount),
                    "method": method
                },
                target="role",
                target_id=role.value
            )
        self.events.emit(
            restaurant_id=restaurant_id,
            event_type="CASH_REGISTER_UPDATED",
            payload={"order_id": order_id},
            target="role",
            target_id=UserRole.CASHIER.value
        )
        return {"deleted": payment_id}

    # -------------------------
    # Cerrar orden
    # -------------------------
    def close_order(self, order: Order) -> OrderResponse:
        if order.status == OrderStatus.CLOSED:
            raise DomainError(
                "La orden ya está cerrada",
                ErrorCode.ORDER_ALREADY_CLOSED
            )
        subtotal, total, total_paid, remaining = self._calculate_totals(order)
        if remaining > 0:
            raise DomainError(
                f"La orden no está paga. Saldo: {remaining:.2f}",
                ErrorCode.ORDER_HAS_REMAINING_BALANCE,
                context={"remaining": money(remaining)}
            )
        if not order.items:
            raise DomainError(
                "La orden no tiene items",
                ErrorCode.ORDER_EMPTY
            )
        not_delivered = [
            i for i in order.items
            if i.status not in [OrderItemStatus.DELIVERED, OrderItemStatus.CANCELLED]
        ]
        if not_delivered:
            raise DomainError(
                "No se puede cerrar la orden. Hay items no entregados",
                ErrorCode.ORDER_ITEMS_NOT_DELIVERED,
                context={"items": [i.id for i in not_delivered]}
            )
        logger.info("Orden cerrada order_id=%s r=%s total=%s", order.id, order.restaurant_id, total)
        self._set_status(order, OrderStatus.CLOSED)
        order.closed_at = func.now()
        self.db.commit()
        self.db.refresh(order)
        # Emitir evento
        for role in [UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER]:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type="ORDER_CLOSED",
                payload={"order_id": order.id},
                target="role",
                target_id=role.value
            )
        self.events.emit(
            restaurant_id=order.restaurant_id,
            event_type="CASH_REGISTER_UPDATED",
            payload={"order_id": order.id},
            target="role",
            target_id=UserRole.CASHIER.value
        )
        return self.to_order_response(order)

    # -------------------------
    # Eliminar item de la orden
    # -------------------------
    def delete_order_item(
        self,
        restaurant_id: int,
        order_id: int,
        item_id: int,
    ) -> None:
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
                context={"item": item_id}
            )
        if item.order_id != order_id:
            raise DomainError(
                "Item no pertenece a la orden",
                ErrorCode.ITEM_NOT_IN_ORDER,
                context={
                    "item": item_id,
                    "order_id": order_id
                }
            )       
        if item.status != OrderItemStatus.PENDING:
            raise DomainError(
                "El item ya fue enviado a la cocina",
                ErrorCode.ITEM_ALREADY_SENT,
                context={"item": item.id}
            )

        order = item.order

        self.db.delete(item)
        new_status = self._calculate_order_status(order)
        self._set_status(order, new_status)
        self.db.commit()
        self.db.refresh(order)
        logger.info("Item eliminado order_id=%s item_id=%s", order_id, item_id)
        # 🔔 EVENTO
        for role in [UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER]:
            self.events.emit(
                restaurant_id=restaurant_id,
                event_type="ORDER_UPDATED",
                payload={"order_id": order_id},
                target="role",
                target_id=role.value
            )

    # -------------------------
    # Actualizar cantidad por item de la orden
    # -------------------------
    def update_item_quantity(
        self,
        restaurant_id: int,
        item_id: int,
        quantity: int
    ) -> OrderResponse:
        item = (
            self.db.query(OrderItem)
            .join(Order)
            .filter(
                OrderItem.id == item_id,
                Order.restaurant_id == restaurant_id
            )
            .first()
        )
        if not item:
            raise DomainError(
                "order item not found",
                ErrorCode.ITEM_NOT_FOUND
            )
        order = item.order
        if item.status != OrderItemStatus.PENDING:
            raise DomainError(
                "cannot modify item already sent to kitchen",
                ErrorCode.ITEM_ALREADY_SENT
            )
        if quantity <= 0:
            return self.delete_order_item(
                restaurant_id,
                item.order_id,
                item.id
            )
        item.quantity = quantity
        new_status = self._calculate_order_status(order)
        self._set_status(order, new_status)
        self.db.commit()
        self.db.refresh(order)
        return self.to_order_response(order)