from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItemStatus
from app.models.payment import Payment
from app.models.user import User
from app.models.order_item import OrderItem


from app.domain.order_transitions import is_valid_order_transition


class OrderDomainError(Exception):
    pass


class OrderService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Cálculos
    # -------------------------

    def calculate_totals(self, order: Order):
        total = sum(
            item.quantity * item.unit_price
            for item in order.items
        )

        total_paid = sum(
            payment.amount
            for payment in order.payments
        )

        remaining = total - total_paid

        return (
            float(total),
            float(total_paid),
            float(remaining)
        )
    
    # -------------------------
    # Enviar a cocina
    # -------------------------

    def send_to_kitchen(self, order: Order):

        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError("Order is closed")

        pending_items = [
            item for item in order.items
            if item.status == OrderItemStatus.PENDING
        ]

        if not pending_items:
            raise OrderDomainError("No pending items to send")

        for item in pending_items:
            item.status = OrderItemStatus.SENT

        if order.status == OrderStatus.OPEN:
            order.status = OrderStatus.SENT

    # -------------------------
    # Cerrar orden
    # -------------------------

    def close_order(self, order: Order):

        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError("Order already closed")

        total, total_paid, remaining = self.calculate_totals(order)

        if remaining > 0:
            raise OrderDomainError(
                f"Order not fully paid. Remaining: {remaining}"
            )

        not_delivered = [
            item for item in order.items
            if item.status != OrderItemStatus.DELIVERED
        ]

        if not_delivered:
            raise OrderDomainError(
                "All items must be DELIVERED before closing order"
            )

        order.status = OrderStatus.CLOSED
        order.closed_at = func.now()

    # -------------------------
    # Registrar pago
    # -------------------------

    def add_payment(self, order: Order, amount, method, cash_register):

        if order.status == OrderStatus.CLOSED:
            raise OrderDomainError("Order already closed")

        total, total_paid, remaining = self.calculate_totals(order)

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
                Order.status != OrderStatus.CLOSED
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

        if not is_valid_order_transition(order.status, new_status):
            raise OrderDomainError("Invalid status transition")

        order.status = new_status


    def add_item(self, order, product, quantity: int):

        if order.status != OrderStatus.OPEN:
            raise OrderDomainError("Cannot add items to a non-open order")

        if quantity <= 0:
            raise OrderDomainError("Quantity must be greater than zero")

        existing_item = next(
            (item for item in order.items if item.product_id == product.id),
            None
        )

        if existing_item:
            existing_item.quantity += quantity
            return existing_item

        new_item = OrderItem(
            restaurant_id=order.restaurant_id,
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=product.price,
            status=OrderItemStatus.PENDING
        )

        self.db.add(new_item)
        return new_item