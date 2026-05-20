# app/utils/money.py

from decimal import Decimal, ROUND_HALF_UP


TWOPLACES = Decimal("0.01")


def to_decimal(value) -> Decimal:
    """
    Convierte input a Decimal seguro.
    """
    return Decimal(str(value))


def money(value) -> str:
    """
    Convierte un valor numérico a string monetario.
    """
    if value is None:
        value = Decimal("0")

    if not isinstance(value, Decimal):
        value = Decimal(str(value))

    return str(value.quantize(TWOPLACES, rounding=ROUND_HALF_UP))