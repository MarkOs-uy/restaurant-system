"""
tests/unit/test_order_service.py

Fase 2 (P0) del plan de testing: totales, transiciones de estado
y flujo de pagos de órdenes.

Correr con: docker compose exec backend pytest tests/unit/test_order_service.py -v
"""

from decimal import Decimal

import pytest
from app.domain.order.order_service import OrderService
from app.domain.cash_register.cash_register_service import CashRegisterService
from app.domain.errors.base import DomainError
from app.models.order import OrderStatus
from app.models.order_item import OrderItemStatus
from app.schemas.order.payment import PaymentCreate
from app.models.payment import PaymentMethod

from .factories import crear_item


# --------------------------------------------------------------------------------
# _calculate_totals
# --------------------------------------------------------------------------------

def test_calculate_totals_suma_items_correctamente(db, restaurant, order, product):
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, quantity=2, unit_price=Decimal("100.00"))
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, quantity=1, unit_price=Decimal("50.00"))
    db.refresh(order)

    subtotal, total, total_paid, remaining = service._calculate_totals(order)

    assert subtotal == Decimal("250.00")  # 2*100 + 1*50
    assert total == Decimal("250.00")     # sin descuento
    assert total_paid == Decimal("0")
    assert remaining == Decimal("250.00")


def test_calculate_totals_aplica_descuento_al_total(db, restaurant, order, product):
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, quantity=1, unit_price=Decimal("100.00"))
    order.discount = Decimal("20.00")
    db.commit()
    db.refresh(order)

    subtotal, total, total_paid, remaining = service._calculate_totals(order)

    assert subtotal == Decimal("100.00")
    assert total == Decimal("80.00")
    assert remaining == Decimal("80.00")


# --------------------------------------------------------------------------------
# apply_discount
# --------------------------------------------------------------------------------

def test_apply_discount_rechaza_descuento_mayor_al_subtotal(db, restaurant, order, product):
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, quantity=1, unit_price=Decimal("100.00"))
    db.refresh(order)

    with pytest.raises(DomainError):
        service.apply_discount(order, Decimal("150.00"))


def test_apply_discount_rechaza_si_deja_pagos_excedidos(db, restaurant, user, order, product):
    """
    Caso real: ya se pagó $80 sobre un total de $100. Si después
    intentan aplicar un descuento de $30, el nuevo total ($70) quedaría
    por debajo de lo ya pagado -- eso no puede pasar.
    """
    service = OrderService(db)
    cash_service = CashRegisterService(db)
    cash_service.open_cash_register(restaurant.id, user.id, Decimal("0"))

    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, quantity=1, unit_price=Decimal("100.00"))
    db.refresh(order)
    service.add_payment(order, PaymentCreate(amount=Decimal("80.00"), method=PaymentMethod.CASH))
    db.refresh(order)

    with pytest.raises(DomainError):
        service.apply_discount(order, Decimal("30.00"))


def test_apply_discount_rechaza_en_orden_cerrada(db, restaurant, order, product):
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, quantity=1, unit_price=Decimal("100.00"),
               status=OrderItemStatus.DELIVERED)
    db.refresh(order)
    order.status = OrderStatus.CLOSED
    db.commit()

    with pytest.raises(DomainError):
        service.apply_discount(order, Decimal("10.00"))


# --------------------------------------------------------------------------------
# _calculate_order_status -- la matriz de estados
# --------------------------------------------------------------------------------

def test_status_todos_cancelados_orden_open_pasa_a_cancelled(db, restaurant, order, product):
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, status=OrderItemStatus.CANCELLED)
    db.refresh(order)

    nuevo_estado = service._calculate_order_status(order)

    assert nuevo_estado == OrderStatus.CANCELLED


def test_status_item_in_progress_domina_sobre_pending(db, restaurant, order, product):
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, status=OrderItemStatus.IN_PROGRESS)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, status=OrderItemStatus.PENDING)
    db.refresh(order)

    nuevo_estado = service._calculate_order_status(order)

    assert nuevo_estado == OrderStatus.IN_PROGRESS


def test_status_todos_ready_o_delivered_es_ready(db, restaurant, order, product):
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, status=OrderItemStatus.READY)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, status=OrderItemStatus.DELIVERED)
    db.refresh(order)

    nuevo_estado = service._calculate_order_status(order)

    assert nuevo_estado == OrderStatus.READY


# --------------------------------------------------------------------------------
# close_order -- los tres guardas
# --------------------------------------------------------------------------------

def test_close_order_rechaza_con_saldo_pendiente(db, restaurant, order, product):
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("100.00"),
               status=OrderItemStatus.DELIVERED)
    db.refresh(order)

    with pytest.raises(DomainError):
        service.close_order(order)


def test_close_order_rechaza_orden_sin_items(db, restaurant, order):
    service = OrderService(db)

    with pytest.raises(DomainError):
        service.close_order(order)


def test_close_order_rechaza_items_no_entregados(db, restaurant, user, order, product):
    service = OrderService(db)
    cash_service = CashRegisterService(db)
    cash_service.open_cash_register(restaurant.id, user.id, Decimal("0"))

    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("100.00"),
               status=OrderItemStatus.READY)  # READY, no DELIVERED
    db.refresh(order)
    service.add_payment(order, PaymentCreate(amount=Decimal("100.00"), method=PaymentMethod.CASH))
    db.refresh(order)

    with pytest.raises(DomainError):
        service.close_order(order)


def test_close_order_ok_con_items_cancelados_y_delivered_mixtos(db, restaurant, user, order, product):
    """
    Un item CANCELLED no cuenta ni para el estado (ya lo cubre
    _calculate_order_status) ni para el total a pagar (fix aplicado
    en _calculate_totals) -- la orden cierra pagando solo el item
    DELIVERED ($100), sin el cancelado ($50).
    """
    service = OrderService(db)
    cash_service = CashRegisterService(db)
    cash_service.open_cash_register(restaurant.id, user.id, Decimal("0"))

    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("100.00"),
               status=OrderItemStatus.DELIVERED)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("50.00"),
               status=OrderItemStatus.CANCELLED)
    db.refresh(order)
    service.add_payment(order, PaymentCreate(amount=Decimal("100.00"), method=PaymentMethod.CASH))
    db.refresh(order)
    # crear_item es un atajo de test que no dispara _set_status como lo
    # haría el flujo real (add_item -> send_to_kitchen -> deliver_item).
    # Simulamos acá el estado al que naturalmente habría llegado la orden.
    order.status = OrderStatus.READY
    db.commit()
    db.refresh(order)

    resultado = service.close_order(order)

    assert resultado.status == OrderStatus.CLOSED


def test_calculate_totals_excluye_items_cancelados(db, restaurant, order, product):
    """
    Regresión del fix: _calculate_totals debe excluir items CANCELLED
    del subtotal, igual que ya hace report_service._order_total y
    _calculate_order_status. Antes del fix este test daba 150.00.
    """
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("100.00"),
               status=OrderItemStatus.DELIVERED)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("50.00"),
               status=OrderItemStatus.CANCELLED)
    db.refresh(order)

    subtotal, total, total_paid, remaining = service._calculate_totals(order)

    assert subtotal == Decimal("100.00")
    assert total == Decimal("100.00")


# --------------------------------------------------------------------------------
# add_payment / delete_payment
# --------------------------------------------------------------------------------

def test_add_payment_rechaza_si_excede_saldo_restante(db, restaurant, user, order, product):
    service = OrderService(db)
    cash_service = CashRegisterService(db)
    cash_service.open_cash_register(restaurant.id, user.id, Decimal("0"))

    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("100.00"))
    db.refresh(order)

    with pytest.raises(DomainError):
        service.add_payment(order, PaymentCreate(amount=Decimal("150.00"), method=PaymentMethod.CASH))


def test_add_payment_requiere_caja_abierta(db, restaurant, order, product):
    """
    Sin caja abierta, add_payment debe fallar -- es el acoplamiento
    real entre OrderService y CashRegisterService.
    """
    service = OrderService(db)
    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("100.00"))
    db.refresh(order)

    with pytest.raises(DomainError):
        service.add_payment(order, PaymentCreate(amount=Decimal("50.00"), method=PaymentMethod.CASH))


def test_add_payment_rechaza_en_orden_cerrada(db, restaurant, order):
    service = OrderService(db)
    order.status = OrderStatus.CLOSED
    db.commit()

    with pytest.raises(DomainError):
        service.add_payment(order, PaymentCreate(amount=Decimal("10.00"), method=PaymentMethod.CASH))


def test_delete_payment_bloqueado_en_orden_cerrada(db, restaurant, user, order, product):
    service = OrderService(db)
    cash_service = CashRegisterService(db)
    cash_service.open_cash_register(restaurant.id, user.id, Decimal("0"))

    crear_item(db, restaurant_id=restaurant.id, order_id=order.id,
               product_id=product.id, unit_price=Decimal("100.00"),
               status=OrderItemStatus.DELIVERED)
    db.refresh(order)
    pago = service.add_payment(order, PaymentCreate(amount=Decimal("100.00"), method=PaymentMethod.CASH))
    db.refresh(order)
    # Mismo motivo que en el test anterior: simulamos el estado READY
    # al que se llegaría vía el flujo real antes de cerrar.
    order.status = OrderStatus.READY
    db.commit()
    db.refresh(order)
    service.close_order(order)

    with pytest.raises(DomainError):
        service.delete_payment(restaurant.id, pago.id)
