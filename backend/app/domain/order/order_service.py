from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from decimal import Decimal, ROUND_HALF_UP
import logging

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product
from app.models.user import UserRole
from app.models.payment import Payment
from app.models.table import Table

from app.services.event_service import EventService
from app.domain.order.order_transitions import is_valid_order_transition
from app.domain.order.constants import ACTIVE_ORDER_STATUSES
from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode
from app.utils.money import money

logger = logging.getLogger("app.domain.order")

class OrderService:

    def __init__(self, db: Session):
        self.db = db
        self.events = EventService(db)

    # -------------------------
    # Getters
    # -------------------------

    # -------------------------
    # Obtener orden por id
    # -------------------------
    def get_order(self, order_id: int, restaurant_id: int):
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
        subtotal, total, total_paid, remaining = self.calculate_totals(order)
        return order

    # -------------------------
    # Obtener ordenes activas
    # -------------------------
    def get_active_orders(self, restaurant_id: int):
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
    def get_active_order(self, restaurant_id: int, table_id: int):
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
    # Serialización
    # -------------------------
    def serialize_order(self, order: Order):
        subtotal, total, total_paid, remaining = self.calculate_totals(order)
        return {
            "id": order.id,
            "table_id": order.table_id,
            "table_number": order.table.number,
            "status": order.status.value,
            "created_at": order.created_at,
            "items": [
                {
                    "id": item.id,
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "unit_price": money(item.unit_price),
                    "subtotal": money(item.quantity * item.unit_price),
                    "status": item.status.value
                }
                for item in order.items
            ],
            "payments": [
                {
                    "id": p.id,
                    "amount": money(p.amount),
                    "method": p.method
                }
                for p in order.payments
            ],
            "total": money(total),
            "subtotal": money(subtotal),
            "discount": money(order.discount or 0),
            "total_paid": money(total_paid),
            "remaining": money(remaining)
        }

    # -------------------------
    # Serializar ordenes activas
    # -------------------------
    def serialize_orders(self, restaurant_id: int):
        orders = self.get_active_orders(restaurant_id)

        result = []

        for order in orders:
            subtotal, total, total_paid, remaining = self.calculate_totals(order)

            result.append({
                "id": order.id,
                "table_id": order.table_id,
                "table_number": order.table.number,
                "status": order.status,
                "created_at": order.created_at,
                "items": [
                    {
                        "id": item.id,
                        "product_name": item.product.name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "subtotal": item.quantity * item.unit_price,
                        "status": item.status
                    }
                    for item in order.items
                ],
                "total": total,
                "subtotal": subtotal,
                "discount": money(order.discount or 0),
                "total_paid": total_paid,
                "remaining": remaining
            })
        return result

    # -------------------------
    # Totales
    # -------------------------
    # -------------------------
    # Calcular totales de la orden
    # -------------------------
    def calculate_totals(self, order: Order):
        subtotal = sum((item.quantity * item.unit_price for item in order.items), Decimal("0"))
        discount = order.discount or Decimal("0")
        total = max(subtotal - discount, Decimal("0"))
        total_paid = sum(payment.amount for payment in order.payments)
        remaining = total - total_paid
        return subtotal, total, total_paid, remaining

    # -------------------------
    # Descuentos
    # -------------------------
    # -------------------------
    # Aplicar descuento a la orden
    # -------------------------
    def apply_discount(self, order: Order, discount: Decimal):
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
        subtotal, _, total_paid, _ = self.calculate_totals(order)
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
        return self.serialize_order(order)

    # -------------------------
    # Crear / agregar items
    # -------------------------
    def add_item(self, order: Order, product_id: int, quantity: int) -> OrderItem:
        if order.status == OrderStatus.CLOSED:
            raise DomainError(
                "Cannot add items to closed order",
                ErrorCode.ORDER_ALREADY_CLOSED
            )
        if quantity <= 0:
            raise DomainError(
                "Quantity must be greater than zero",
                ErrorCode.INVALID_OPERATION
            )
        # Buscar producto en la base
        product = (
            self.db.query(Product)
            .filter(
                Product.id == product_id,
                Product.restaurant_id == order.restaurant_id,
                Product.active
            )
            .first()
        )
        if not product:
            raise DomainError(
                "Product not found",
                ErrorCode.ITEM_NOT_FOUND,
                context={"product_id": product_id}
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
        
        self.db.flush()  # Asegura que item.id esté disponible  
        self.recalculate_order_status(order)      
        
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

        self.db.commit()
        self.db.refresh(item)
        self.db.refresh(order)
        return item

    # -------------------------
    # Agregar producto a la mesa (crear orden si no existe)
    # -------------------------
    def add_product_to_table(self, restaurant_id: int, table_id: int, product_id: int, quantity: int):
        table = self.db.query(Table).filter(Table.id == table_id, Table.restaurant_id == restaurant_id).first()
        if not table:
            raise DomainError(
                "Table not found",
                ErrorCode.TABLE_NOT_FOUND
            )

        order = self.get_active_order(restaurant_id, table_id)
        if not order:
            order = Order(table_id=table_id, restaurant_id=restaurant_id, status=OrderStatus.OPEN)
            self.db.add(order)
            self.db.flush()

        product = self.db.query(Product).filter(Product.id == product_id, Product.restaurant_id == restaurant_id, Product.active).first()
        if not product:
            raise DomainError(
                "Product not found",
                ErrorCode.ITEM_NOT_FOUND,
                context={"product_id": product_id}
            )

        item = self.add_item(order, product.id, quantity)
        return {"order_id": order.id, "item_id": item.id}


    # -------------------------
    # Estados
    # -------------------------
    # -------------------------
    # Actualizar estado de la orden
    # -------------------------
    def update_status(self, order: Order, new_status: OrderStatus):
        if order.status == new_status:
            return order
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
        previous_status = order.status
        order.status = new_status
        logger.info("Estado de orden actualizado order_id=%s from=%s to=%s", order.id, previous_status.value, new_status.value)
        # Emit events solo si cambio
        if previous_status != new_status:
            for role in [UserRole.ADMIN, UserRole.WAITER]:
                self.events.emit(
                    restaurant_id=order.restaurant_id,
                    event_type="ORDER_STATUS_CHANGED",
                    payload={"order_id": order.id, "status": new_status.value},
                    target="role",
                    target_id=role.value
                )

        for role in [UserRole.ADMIN, UserRole.WAITER]:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type="ORDER_UPDATED",
                payload={"order_id": order.id},
                target="role",
                target_id=role.value
            )
        self.db.commit()
        self.db.refresh(order)
        return order

    # -------------------------
    # Recalcular estado de la orden basado en estados de los items
    # -------------------------
    def recalculate_order_status(self, order: Order):
        active_items = [
            i for i in order.items
            if i.status != OrderItemStatus.CANCELLED
        ]

        if not active_items:
            # Si todos los ítems fueron cancelados y la orden
            # todavía no fue enviada a cocina, se cancela automáticamente.
            # En estados posteriores (SENT, IN_PROGRESS, etc.) esto
            # no puede ocurrir porque siempre hay ítems activos.
            if order.status in [OrderStatus.DRAFT, OrderStatus.OPEN]:
                self.update_status(order, OrderStatus.CANCELLED)
            return

        statuses = [i.status for i in active_items]

        if any(s == OrderItemStatus.IN_PROGRESS for s in statuses):
            self.update_status(order, OrderStatus.IN_PROGRESS)
        elif any(s == OrderItemStatus.SENT for s in statuses):
            self.update_status(order, OrderStatus.SENT)
        elif any(s == OrderItemStatus.PENDING for s in statuses):
            self.update_status(order, OrderStatus.OPEN)
        elif all(s in [OrderItemStatus.READY, OrderItemStatus.DELIVERED] for s in statuses):
            self.update_status(order, OrderStatus.READY)

    # -------------------------
    # Enviar a cocina
    # -------------------------
    def send_to_kitchen(self, order: Order):
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
        self.recalculate_order_status(order)
        # Agrupar por estación y emitir
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
        self.db.commit()
        # 🔹 Convertir a JSON serializable
        result = [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": money(item.unit_price),
                "status": item.status.value,
                "subtotal": money(item.quantity * item.unit_price)
            }
            for item in pending_items
        ]
        return result

    # -------------------------
    # Pagos
    # -------------------------

    def add_payment(self, order: Order, amount: Decimal, method: str):
        from app.domain.cash_register.cash_register_service import CashRegisterService

        if order.status == OrderStatus.CLOSED:
            raise DomainError(
                "Order already closed",
                ErrorCode.ORDER_ALREADY_CLOSED
            )

        cash_service = CashRegisterService(self.db)
        cash_register = cash_service.require_open_cash_register(order.restaurant_id)

        subtotal, total, total_paid, remaining = self.calculate_totals(order)
        if amount > remaining:
            raise DomainError(
                "Payment exceeds remaining balance",
                ErrorCode.PAYMENT_EXCEEDS_REMAINING,
                context={
                    "amount": money(amount),
                    "remaining": money(remaining)
                }
            )
        logger.info("Pago agregado order_id=%s amount=%s method=%s", order.id, amount, method)
        payment = Payment(
            order_id=order.id,
            restaurant_id=order.restaurant_id,
            amount=amount,
            method=method,
            cash_register_id=cash_register.id
        )
        self.db.add(payment)

        # Emitir eventos
        for role in [UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER]:
            self.events.emit(
                restaurant_id=order.restaurant_id,
                event_type="PAYMENT_ADDED",
                payload={"order_id": order.id, "amount": money(amount), "method": method},
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
        self.db.commit()
        self.db.refresh(payment)
        return payment

    # -------------------------
    # Cancelar pago
    # -------------------------
    def cancel_payment(self, restaurant_id: int, payment_id: int):
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
                "Cannot cancel payment from closed order",
                ErrorCode.INVALID_OPERATION
            )
        logger.info("Pago cancelado order_id=%s amount=%s method=%s", payment.order_id, payment.amount, payment.method)
        order_id = payment.order_id
        amount = payment.amount
        method = payment.method

        self.db.delete(payment)

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
        self.db.commit()
        return {"deleted": payment_id}

    # -------------------------
    # Cerrar orden
    # -------------------------
    def close_order(self, order: Order):

        if order.status == OrderStatus.CLOSED:
            raise DomainError(
                "La orden ya está cerrada",
                ErrorCode.ORDER_ALREADY_CLOSED
            )

        subtotal, total, total_paid, remaining = self.calculate_totals(order)

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

        not_delivered = [i for i in order.items if i.status != OrderItemStatus.DELIVERED]

        if not_delivered:
            raise DomainError(
                "No se puede cerrar la orden. Hay items no entregados",
                ErrorCode.ORDER_ITEMS_NOT_DELIVERED,
                context={"items": [i.id for i in not_delivered]}
            )
        logger.info("Orden cerrada order_id=%s r=%s total=%s", order.id, order.restaurant_id, total)
        self.update_status(order, OrderStatus.CLOSED)
        order.closed_at = func.now()

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
        self.db.commit()
        return order

    # -------------------------
    # Eliminar item de la orden
    # -------------------------
    def delete_order_item(
        self,
        restaurant_id: int,
        order_id: int,
        item_id: int,
    ):
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
        order = (
            self.db.query(Order)
            .filter(
                Order.id == order_id,
                Order.restaurant_id == restaurant_id
            )
            .first()
        )

        self.db.delete(item)
        self.recalculate_order_status(order)
        # 🔔 EVENTO
        for role in [UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER]:
            self.events.emit(
                restaurant_id=restaurant_id,
                event_type="ORDER_UPDATED",
                payload={"order_id": order_id},
                target="role",
                target_id=role.value
            )
        self.db.commit()
        return {"message": "Item eliminado"}

    # -------------------------
    # Actualizar cantidad por item de la orden
    # -------------------------
    def update_item_quantity(
        self,
        restaurant_id: int,
        item_id: int,
        quantity: int
    ):
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

        if item.status != OrderItemStatus.PENDING:
            raise DomainError(
                "cannot modify item already sent to kitchen",
                ErrorCode.ITEM_ALREADY_SEND
            )
        if quantity <= 0:
            return self.delete_order_item(
                restaurant_id,
                item.order_id,
                item.id
            )
        item.quantity = quantity
        self.db.commit()
        return {
            "id": item.id,
            "quantity": item.quantity
        }
