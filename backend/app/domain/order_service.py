from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from decimal import Decimal

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItemStatus
from app.models.user import UserRole
from app.models.payment import Payment
from app.websocket.manager import manager
from app.models.order_item import OrderItem

from app.domain.order_transitions import is_valid_order_transition
from backend.app.services.event_service import event_service

import asyncio

class OrderDomainError(Exception):
    pass


class OrderService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Cálculos
    # -------------------------

    def calculate_totals(self, order: Order):
        from decimal import Decimal

        subtotal = sum(
            item.quantity * item.unit_price
            for item in order.items
        )

        discount = order.discount or Decimal("0")

        total = subtotal - discount

        if total < 0:
            total = Decimal("0")

        total_paid = sum(
            payment.amount
            for payment in order.payments
        )

        remaining = total - total_paid

        return (
            float(subtotal),
            float(total),
            float(total_paid),
            float(remaining)
        )
    
    # -------------------------
    # Enviar a cocina
    # -------------------------

    def send_to_kitchen(self, order: Order):

        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError("La orden está cerrada")

        # 👉 obtener items pendientes
        pending_items = [
            item for item in order.items
            if item.status == OrderItemStatus.PENDING
        ]

        if not pending_items:
            raise OrderDomainError("No hay items pendientes de envío")

        # 🔄 cambiar estado de items
        for item in pending_items:
            item.status = OrderItemStatus.SENT

        # 🔥 recalcular estado de la orden (UNIFICADO)
        previous_status = order.status
        self.recalculate_order_status(order)

        # =========================
        # 🔔 EVENTOS
        # =========================

        import asyncio

        # 👉 agrupar por estación (clave para no spamear)
        station_ids = {
            item.product.station_id
            for item in pending_items
        }

        # 👉 cocina
        for station_id in station_ids:
            event_service.emit_to_station(
                order.restaurant_id,
                station_id,
                {
                    "type": "ORDER_UPDATED",
                    "order_id": order.id
                }
            )

        # 👉 mozos (solo si cambia estado)
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

        return pending_items


    # -------------------------
    # Cerrar orden
    # -------------------------

    def close_order(self, order: Order):

        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError("Order already closed")

        subtotal, total, total_paid, remaining = self.calculate_totals(order)

        if remaining > 0:
            raise OrderDomainError(
                f"Order not fully paid. Remaining: {remaining:.2f}"
            )

        if not order.items:
            raise OrderDomainError("Order has no items")

        # 🔍 validar items entregados
        not_delivered = [
            {
                "id": item.id,
                "status": item.status.value if hasattr(item.status, "value") else str(item.status)
            }
            for item in order.items
            if item.status != OrderItemStatus.DELIVERED
        ]

        # 🔎 debug útil
        print("ORDER ID:", order.id)
        print("ITEM STATES:", [
            (item.id, str(item.status))
            for item in order.items
        ])

        if not_delivered:
            raise OrderDomainError(
                f"No se puede cerrar la orden. Hay items no entregados. Items: {not_delivered}"
            )

        # ✅ transición correcta
        self.update_status(order, OrderStatus.CLOSED)
        order.closed_at = func.now()

        # =========================
        # 🔔 EVENTO: ORDEN CERRADA
        # =========================

        event_service.emit_to_role(
            order.restaurant_id,
            UserRole.WAITER,
            {
                "type": "ORDER_CLOSED",
                "order_id": order.id
            }
        )


    # -------------------------
    # Registrar pago
    # -------------------------

    def add_payment(self, order: Order, amount, method, cash_register):

        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError("Order already closed")

        subtotal, total, total_paid, remaining = self.calculate_totals(order)

        if amount > remaining:
            raise OrderDomainError(
                "Payment exceeds remaining balance"
            )

        payment = Payment(
            order_id=order.id,
            restaurant_id=order.restaurant_id,
            amount=amount,
            method=method,
            cash_register_id=cash_register.id
        )

        self.db.add(payment)


    def get_active_orders(self, restaurant_id: int):
        return (
            self.db.query(Order)
            .options(
                joinedload(Order.items).joinedload(OrderItem.product),
                joinedload(Order.payments),
                joinedload(Order.table)
            )
            .filter(
                Order.restaurant_id == restaurant_id,
                Order.status.in_([
                    OrderStatus.OPEN,
                    OrderStatus.SENT,
                    OrderStatus.IN_PROGRESS,
                    OrderStatus.READY
                ])
            )
            .all()
        )


    def get_order(self, order_id: int, restaurant_id: int):

        order = (
            self.db.query(Order)
            .options(
                joinedload(Order.items).joinedload(OrderItem.product),
                joinedload(Order.payments),
                joinedload(Order.table)
            )
            .filter(
                Order.id == order_id,
                Order.restaurant_id == restaurant_id
            )
            .first()
        )

        if not order:
            raise OrderDomainError("Order not found")

        return order


    def update_status(self, order: Order, new_status: OrderStatus):

        if order.status == new_status:
            return order

        if not is_valid_order_transition(order.status, new_status):
            raise OrderDomainError(
                f"Invalid transition: {order.status} → {new_status}"
            )

        order.status = new_status

        return order


    def add_item(self, order, product, quantity: int):

        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError("No se pueden agregar items a una orden cerrada")

        if quantity <= 0:
            raise OrderDomainError("La cantidad debe ser mayor a 0 (cero)")

        existing_item = self.db.query(OrderItem).filter(
            OrderItem.order_id == order.id,
            OrderItem.product_id == product.id,
            OrderItem.status == OrderItemStatus.PENDING
        ).first()

        if existing_item:
            existing_item.quantity += quantity
            item = existing_item
        else:
            item = OrderItem(
                restaurant_id=order.restaurant_id,
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=product.price,
                status=OrderItemStatus.PENDING
            )
            self.db.add(item)

        # 🔥 recalcular estado de orden
        previous_status = order.status
        self.recalculate_order_status(order)

        # =========================
        # 🔔 EVENTOS
        # =========================

        # 👉 cocina
        event_service.emit_to_station(
            order.restaurant_id,
            product.station_id,
            {
                "type": "NEW_ITEM",
                "order_id": order.id
            }
        )

        # 👉 mozos (esto te faltaba)
        event_service.emit_to_role(
            order.restaurant_id,
            UserRole.WAITER,
            {
                "type": "ORDER_UPDATED",
                "order_id": order.id
            }
        )

        return item


    def recalculate_order_status(self, order: Order):

        items = order.items

        if not items:
            return order

        # ❗ ignorar cancelados
        active_items = [
            item for item in items
            if item.status != OrderItemStatus.CANCELLED
        ]

        # si todos fueron cancelados
        if not active_items:
            self.update_status(order, OrderStatus.CANCELLED)
            return order

        statuses = [item.status for item in active_items]

        # 🔴 PRIORIDAD 1
        if any(s == OrderItemStatus.IN_PROGRESS for s in statuses):
            self.update_status(order, OrderStatus.IN_PROGRESS)
            return order

        # 🟠 PRIORIDAD 2
        if any(s == OrderItemStatus.SENT for s in statuses):
            self.update_status(order, OrderStatus.SENT)
            return order

        # 🟡 PRIORIDAD 3
        if any(s == OrderItemStatus.PENDING for s in statuses):
            self.update_status(order, OrderStatus.OPEN)
            return order

        # 🟢 PRIORIDAD 4
        if all(s in [OrderItemStatus.READY, OrderItemStatus.DELIVERED] for s in statuses):
            self.update_status(order, OrderStatus.READY)
            return order

        return order