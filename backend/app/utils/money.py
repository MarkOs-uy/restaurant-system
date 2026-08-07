from decimal import Decimal, ROUND_HALF_UP
from typing import Any

TWOPLACES = Decimal("0.01")


# --------------------------------------------------------------------------------------
# Convierte un valor a Decimal de forma segura.
# --------------------------------------------------------------------------------------
def to_decimal(value: Any) -> Decimal:
    """
    Convierte cualquier valor numérico compatible a Decimal.
    """
    return Decimal(str(value))


# --------------------------------------------------------------------------------------
# Devuelve un valor monetario con dos decimales utilizando ROUND_HALF_UP.
# --------------------------------------------------------------------------------------
def money(value: Any) -> str:
    """
    Convierte un valor numérico a su representación monetaria.
    """

    if value is None:
        value = Decimal("0")

    if not isinstance(value, Decimal):
        value = Decimal(str(value))

    return str(
        value.quantize(
            TWOPLACES,
            rounding=ROUND_HALF_UP,
        )
    )