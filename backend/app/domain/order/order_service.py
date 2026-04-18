from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from decimal import Decimal

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem, OrderItemStatus
from app.models.product import Product
from app.models.user import UserRole
from app.models.payment import Payment
from app.models.table import Table

from app.services.event_service import event_service
from app.domain.order.order_transitions import is_valid_order_transition
from app.domain.order.constants import ACTIVE_ORDER_STATUSES
from app.domain.errors import OrderDomainError
from app.domain.error_codes import ErrorCode


class OrderService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Getters
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
            raise OrderDomainError(
                "Orden no encontrada",
                ErrorCode.ORDER_NOT_FOUND
            )

        subtotal, total, total_paid, remaining = self.calculate_totals(order)

        return order


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


    def serialize_order(self, order: Order):
        subtotal, total, total_paid, remaining = self.calculate_totals(order)
        return {
            "id": order.id,
            "table_id": order.table_id,
            "table_number": order.table.number,
            "status": order.status.value,
            "items": [
                {
                    "id": item.id,
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                    "subtotal": float(item.quantity * item.unit_price),
                    "status": item.status.value
                }
                for item in order.items
            ],
            "payments": [
                {
                    "id": p.id,
                    "amount": float(p.amount),
                    "method": p.method
                }
                for p in order.payments
            ],
            "total": float(total),
            "subtotal": float(subtotal),
            "discount": float(order.discount or 0),
            "total_paid": float(total_paid),
            "remaining": float(remaining)
        }


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
                "discount": float(order.discount or 0),
                "total_paid": total_paid,
                "remaining": remaining
            })

        return result



    # -------------------------
    # Totales
    # -------------------------

    def calculate_totals(self, order: Order):
        subtotal = sum((item.quantity * item.unit_price for item in order.items), Decimal("0"))
        discount = order.discount or Decimal("0")
        total = max(subtotal - discount, Decimal("0"))
        total_paid = sum(payment.amount for payment in order.payments)
        remaining = total - total_paid
        return subtotal, total, total_paid, remaining

    # -------------------------
    # Crear / agregar items
    # -------------------------

    def add_item(self, order: Order, product_id: int, quantity: int) -> OrderItem:
        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError(
                "Cannot add items to closed order",
                ErrorCode.ORDER_ALREADY_CLOSED
            )
        if quantity <= 0:
            raise OrderDomainError(
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
            raise OrderDomainError(
                "Product not found",
                ErrorCode.ITEM_NOT_FOUND,
                context={"product_id": product_id}
            )

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
        
        self.db.commit()
        self.db.refresh(item)

        previous_status = order.status
        self.db.refresh(order)  # Trae la lista de items actualizada
        self.recalculate_order_status(order)

        # =========================
        # 🔔 EVENTOS
        # =========================
        event_service.emit_to_station(
            order.restaurant_id,
            product.station_id,
            {"type": "NEW_ITEM", "order_id": order.id}
        )

        if order.status != previous_status:
            for role in [UserRole.WAITER, UserRole.CASHIER]:
                event_service.emit_to_role(
                    order.restaurant_id,
                    role,
                    {"type": "ORDER_STATUS_CHANGED", "order_id": order.id, "status": order.status.value}
                )

        for role in [UserRole.WAITER, UserRole.CASHIER]:
            print("EVENT emit_to_role en ADD ITEM ORDER_UPDATED")
            event_service.emit_to_role(
                order.restaurant_id,
                role,
                {"type": "ORDER_UPDATED", "order_id": order.id}
            )

        return item


    def add_product_to_table(self, restaurant_id: int, table_id: int, product_id: int, quantity: int):
        table = self.db.query(Table).filter(Table.id == table_id, Table.restaurant_id == restaurant_id).first()
        if not table:
            raise OrderDomainError(
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
            raise OrderDomainError(
                "Product not found",
                ErrorCode.ITEM_NOT_FOUND,
                context={"product_id": product_id}
            )

        item = self.add_item(order, product.id, quantity)
        return {"order_id": order.id, "item_id": item.id}


    # -------------------------
    # Estados
    # -------------------------

    def update_status(self, order: Order, new_status: OrderStatus):
        if order.status == new_status:
            return order

        if not is_valid_order_transition(order.status, new_status):
            raise OrderDomainError(
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

        self.db.commit()
        self.db.refresh(order)

        # Emit events solo si cambio
        if previous_status != new_status:
            event_service.emit_to_role(
                order.restaurant_id,
                UserRole.WAITER,
                {"type": "ORDER_STATUS_CHANGED", "order_id": order.id, "status": new_status.value}
            )

        event_service.emit_to_role(
            order.restaurant_id,
            UserRole.WAITER,
            {"type": "ORDER_UPDATED", "order_id": order.id}
        )
        return order


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
            raise OrderDomainError(
                "Order is closed",
                ErrorCode.ORDER_ALREADY_CLOSED
            )

        pending_items = [i for i in order.items if i.status == OrderItemStatus.PENDING]
        if not pending_items:
            raise OrderDomainError(
                "No pending items to send",
                ErrorCode.NO_PENDING_ITEMS_TO_SEND
            )

        previous_status = order.status
        for item in pending_items:
            item.status = OrderItemStatus.SENT

        self.recalculate_order_status(order)
        self.db.commit()

        # Agrupar por estación y emitir
        station_ids = {i.product.station_id for i in pending_items}
        for station_id in station_ids:
            event_service.emit_to_station(
                order.restaurant_id,
                station_id,
                {"type": "ORDER_UPDATED", "order_id": order.id}
            )

        if order.status != previous_status:
            event_service.emit_to_role(
                order.restaurant_id,
                UserRole.WAITER,
                {"type": "ORDER_STATUS_CHANGED", "order_id": order.id, "status": order.status.value}
            )

        # 🔹 Convertir a JSON serializable
        result = [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "status": item.status.value,
                "subtotal": float(item.quantity * item.unit_price)
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
            raise OrderDomainError(
                "Order already closed",
                ErrorCode.ORDER_ALREADY_CLOSED
            )

        cash_service = CashRegisterService()
        cash_register = cash_service.require_open_cash_register(self.db, order.restaurant_id)

        subtotal, total, total_paid, remaining = self.calculate_totals(order)
        if amount > remaining:
            raise OrderDomainError(
                "Payment exceeds remaining balance",
                ErrorCode.PAYMENT_EXCEEDS_REMAINING,
                context={
                    "amount": float(amount),
                    "remaining": float(remaining)
                }
            )

        payment = Payment(
            order_id=order.id,
            restaurant_id=order.restaurant_id,
            amount=amount,
            method=method,
            cash_register_id=cash_register.id
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)

        # Emitir eventos
        for role in [UserRole.WAITER, UserRole.CASHIER]:
            event_service.emit_to_role(
                order.restaurant_id,
                role,
                {"type": "PAYMENT_ADDED", "order_id": order.id, "amount": float(amount), "method": method}
            )

        event_service.emit_to_role(
            order.restaurant_id,
            UserRole.CASHIER,
            {"type": "CASH_REGISTER_UPDATED"}
        )
        return payment


    def cancel_payment(self, restaurant_id: int, payment_id: int):
        print("Id: ",payment_id)
        payment = (
            self.db.query(Payment)
            .filter(
                Payment.id == payment_id,
                Payment.restaurant_id == restaurant_id
            )
            .first()
        )

        if not payment:
            raise OrderDomainError(
                "Pago no encontrado",
                ErrorCode.PAYMENT_NOT_FOUND
                )

        if payment.order.status == OrderStatus.CLOSED:
            raise OrderDomainError(
                "Cannot cancel payment from closed order",
                ErrorCode.INVALID_OPERATION
            )

        order_id = payment.order_id
        amount = payment.amount
        method = payment.method

        self.db.delete(payment)
        self.db.commit()

        for role in [UserRole.WAITER, UserRole.CASHIER]:
            event_service.emit_to_role(
                restaurant_id,
                role,
                {
                    "type": "PAYMENT_DELETED",
                    "order_id": order_id,
                    "amount": float(amount),
                    "method": method                   
                }
            )

        event_service.emit_to_role(
            restaurant_id,
            UserRole.CASHIER,
            {"type": "CASH_REGISTER_UPDATED"}
        )

        return {"deleted": payment_id}

    # -------------------------
    # Cerrar orden
    # -------------------------

    def close_order(self, order: Order):

        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError(
                "La orden ya está cerrada",
                ErrorCode.ORDER_ALREADY_CLOSED
            )

        subtotal, total, total_paid, remaining = self.calculate_totals(order)

        if remaining > 0:
            raise OrderDomainError(
                f"La orden no está paga. Saldo: {remaining:.2f}",
                ErrorCode.ORDER_HAS_REMAINING_BALANCE,
                context={"remaining": float(remaining)}
            )

        if not order.items:
            raise OrderDomainError(
                "La orden no tiene items",
                ErrorCode.ORDER_EMPTY
            )

        not_delivered = [i for i in order.items if i.status != OrderItemStatus.DELIVERED]

        if not_delivered:
            raise OrderDomainError(
                "No se puede cerrar la orden. Hay items no entregados",
                ErrorCode.ORDER_ITEMS_NOT_DELIVERED,
                context={"items": [i.id for i in not_delivered]}
            )

        self.update_status(order, OrderStatus.CLOSED)
        order.closed_at = func.now()
        self.db.commit()

        # Emitir evento
        for role in [UserRole.WAITER, UserRole.CASHIER]:
            event_service.emit_to_role(
                order.restaurant_id,
                role,
                {"type": "ORDER_CLOSED", "order_id": order.id}
            )

        event_service.emit_to_role(
            order.restaurant_id,
            UserRole.CASHIER,
            {"type": "CASH_REGISTER_UPDATED"}
        )

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
            raise OrderDomainError(
                "Item no encontrado",
                ErrorCode.ITEM_NOT_FOUND,
                context={"item": item_id}
            )

        if item.order_id != order_id:
            raise OrderDomainError(
                "Item no pertenece a la orden",
                ErrorCode.ITEM_NOT_IN_ORDER,
                context={
                    "item": item_id,
                    "order_id": order_id
                }
            )
        
        if item.status != OrderItemStatus.PENDING:
            raise OrderDomainError(
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
        self.db.commit()

        self.recalculate_order_status(order)

        # 🔔 EVENTO
        for role in [UserRole.WAITER, UserRole.CASHIER]:
            event_service.emit_to_role(
                restaurant_id,
                role,
                {"type": "ORDER_UPDATED", "order_id": order_id}
            )

        return {"message": "Item eliminado"}
