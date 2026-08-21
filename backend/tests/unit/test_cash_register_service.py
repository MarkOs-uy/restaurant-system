"""
tests/unit/test_cash_register_service.py

Fase 1 (P0) del plan de testing: dinero y estado de caja.
Correr con: docker compose exec backend pytest tests/unit/test_cash_register_service.py -v
"""

from decimal import Decimal

import pytest
from app.domain.cash_register.cash_register_service import CashRegisterService
from app.domain.errors.base import DomainError
from app.models.payment import PaymentMethod
from app.models.cash_movement import CashMovementType
from app.models.order import OrderStatus
from app.schemas.cash_register import CashRegisterClose

from .factories import crear_pago, crear_movimiento_caja, crear_orden


# --------------------------------------------------------------------------------
# open_cash_register
# --------------------------------------------------------------------------------

def test_open_cash_register_rejects_negative_amount(db, restaurant, user):
    service = CashRegisterService(db)

    with pytest.raises(DomainError):
        service.open_cash_register(
            restaurant_id=restaurant.id,
            user_id=user.id,
            opening_amount=Decimal("-1"),
        )


def test_open_cash_register_rejects_second_open(db, restaurant, user):
    service = CashRegisterService(db)
    service.open_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        opening_amount=Decimal("1000"),
    )

    with pytest.raises(DomainError):
        service.open_cash_register(
            restaurant_id=restaurant.id,
            user_id=user.id,
            opening_amount=Decimal("500"),
        )


# --------------------------------------------------------------------------------
# close_cash_register -- el corazón de la Fase 1
# --------------------------------------------------------------------------------

def test_close_cash_register_expected_cash_solo_cuenta_efectivo(db, restaurant, user, table):
    """
    Caso real que probaste a mano: abrís con $1000, un pago en efectivo
    de $500 y uno con tarjeta de $300. El expected_cash debe ser 1500,
    no 1800 -- la tarjeta no suma al efectivo esperado en caja.
    """
    service = CashRegisterService(db)
    caja = service.open_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        opening_amount=Decimal("1000"),
    )
    orden = crear_orden(db, restaurant_id=restaurant.id, table_id=table.id)

    crear_pago(db, restaurant_id=restaurant.id, cash_register_id=caja.id,
               order_id=orden.id, amount=Decimal("500"), method=PaymentMethod.CASH)
    crear_pago(db, restaurant_id=restaurant.id, cash_register_id=caja.id,
               order_id=orden.id, amount=Decimal("300"), method=PaymentMethod.CARD)

    resultado = service.close_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        data=CashRegisterClose(counted_cash=Decimal("1500")),
    )

    assert resultado.expected_cash == Decimal("1500")
    assert resultado.difference == Decimal("0")
    assert resultado.total_sales == Decimal("800")  # 500 + 300, esto sí suma todo


def test_close_cash_register_difference_negativa_no_bloquea_cierre(db, restaurant, user, table):
    """
    Si el cajero cuenta menos plata de la esperada, el sistema debe
    reportar la diferencia pero NO impedir el cierre -- eso lo decide
    un supervisor después, no el sistema.
    """
    service = CashRegisterService(db)
    caja = service.open_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        opening_amount=Decimal("1000"),
    )
    orden = crear_orden(db, restaurant_id=restaurant.id, table_id=table.id)
    crear_pago(db, restaurant_id=restaurant.id, cash_register_id=caja.id,
               order_id=orden.id, amount=Decimal("500"), method=PaymentMethod.CASH)

    resultado = service.close_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        data=CashRegisterClose(counted_cash=Decimal("1400")),  # faltan $100
    )

    assert resultado.expected_cash == Decimal("1500")
    assert resultado.difference == Decimal("-100")


def test_close_cash_register_bloquea_si_hay_ordenes_abiertas(db, restaurant, user, table):
    service = CashRegisterService(db)
    caja = service.open_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        opening_amount=Decimal("1000"),
    )
    crear_orden(db, restaurant_id=restaurant.id, table_id=table.id, status=OrderStatus.IN_PROGRESS)

    with pytest.raises(DomainError):
        service.close_cash_register(
            restaurant_id=restaurant.id,
            user_id=user.id,
            data=CashRegisterClose(counted_cash=Decimal("1000")),
        )


def test_close_cash_register_rejects_negative_counted_cash(db, restaurant, user):
    """
    OJO: counted_cash ya tiene Field(ge=Decimal("0")) en el schema
    Pydantic (CashRegisterClose), así que el rechazo pasa ACÁ -- al
    construir el objeto -- y nunca llega a pisar el service.

    El chequeo `if data.counted_cash < 0: raise DomainError` que
    tiene close_cash_register es código muerto: Pydantic ya garantiza
    que ese valor nunca puede ser negativo. No es un bug, pero es
    duplicación -- vale la pena limpiarlo en algún refactor.
    """
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CashRegisterClose(counted_cash=Decimal("-50"))


def test_close_cash_register_considera_movimientos_de_caja(db, restaurant, user):
    """
    Un cash_in (ej: cambio que trae el dueño) y un cash_out (ej: pago
    a un proveedor) deben afectar expected_cash en la dirección correcta.
    """
    service = CashRegisterService(db)
    caja = service.open_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        opening_amount=Decimal("1000"),
    )
    crear_movimiento_caja(db, cash_register_id=caja.id, user_id=user.id,
                           amount=Decimal("200"), tipo=CashMovementType.CASH_IN)
    crear_movimiento_caja(db, cash_register_id=caja.id, user_id=user.id,
                           amount=Decimal("50"), tipo=CashMovementType.CASH_OUT)

    resultado = service.close_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        data=CashRegisterClose(counted_cash=Decimal("1150")),
    )

    # 1000 (apertura) + 0 (ventas cash) + 200 (in) - 50 (out) = 1150
    assert resultado.expected_cash == Decimal("1150")
    assert resultado.difference == Decimal("0")


# --------------------------------------------------------------------------------
# average_ticket -- caso límite de división por cero
# --------------------------------------------------------------------------------

def test_average_ticket_es_cero_sin_ordenes(db, restaurant, user):
    """
    Deja escrito en piedra que _calculate_sales no explota si todavía
    no hubo ninguna venta -- por si alguien "optimiza" el código después.
    """
    service = CashRegisterService(db)
    service.open_cash_register(
        restaurant_id=restaurant.id,
        user_id=user.id,
        opening_amount=Decimal("1000"),
    )

    resumen = service.get_current_cash_register(restaurant_id=restaurant.id)

    assert resumen.average_ticket == Decimal("0")
    assert resumen.orders_count == 0