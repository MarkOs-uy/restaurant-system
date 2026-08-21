"""
tests/unit/factories.py

Funciones helper para crear datos de prueba rápido, sin repetir
boilerplate de SQLAlchemy en cada test.

Estas NO son fixtures de pytest -- son funciones normales que se
llaman a mano dentro de cada test, pasándoles la sesión `db`.
"""

from decimal import Decimal

from app.models.payment import Payment, PaymentMethod
from app.models.cash_movement import CashMovement, CashMovementType
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem, OrderItemStatus


def crear_pago(
    db,
    restaurant_id: int,
    cash_register_id: int,
    order_id: int,
    amount: Decimal,
    method: PaymentMethod = PaymentMethod.CASH,
) -> Payment:
    pago = Payment(
        restaurant_id=restaurant_id,
        cash_register_id=cash_register_id,
        order_id=order_id,
        amount=amount,
        method=method,
    )
    db.add(pago)
    db.commit()
    db.refresh(pago)
    return pago


def crear_movimiento_caja(
    db,
    cash_register_id: int,
    user_id: int,
    amount: Decimal,
    tipo: CashMovementType,
    reason: str = "ajuste de prueba",
) -> CashMovement:
    mov = CashMovement(
        cash_register_id=cash_register_id,
        user_id=user_id,
        amount=amount,
        type=tipo,
        reason=reason,
    )
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return mov


def crear_orden(
    db,
    restaurant_id: int,
    table_id: int,
    status: OrderStatus = OrderStatus.CLOSED,
) -> Order:
    """
    Por defecto crea la orden ya CLOSED, porque la mayoría de los
    tests de caja no necesitan una orden abierta -- solo necesitan
    que exista una orden a la que asociar pagos.
    """
    orden = Order(
        restaurant_id=restaurant_id,
        table_id=table_id,
        status=status,
    )
    db.add(orden)
    db.commit()
    db.refresh(orden)
    return orden


def crear_item(
    db,
    restaurant_id: int,
    order_id: int,
    product_id: int,
    quantity: int = 1,
    unit_price: Decimal = Decimal("100.00"),
    status: OrderItemStatus = OrderItemStatus.PENDING,
) -> OrderItem:
    item = OrderItem(
        restaurant_id=restaurant_id,
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        unit_price=unit_price,
        status=status,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item