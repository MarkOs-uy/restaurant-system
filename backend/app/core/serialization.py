from decimal import Decimal
from typing import Any


# --------------------------------------------------------------------------------------
# Convierte un Decimal a float. Si el valor no es Decimal, lo devuelve sin cambios.
# --------------------------------------------------------------------------------------
def decimal_to_float(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return value


# --------------------------------------------------------------------------------------
# Convierte todos los valores Decimal de un diccionario a float.
# --------------------------------------------------------------------------------------
def decimal_dict_to_float(data: dict[str, Any]) -> dict[str, Any]:
    return {
        key: decimal_to_float(value)
        for key, value in data.items()
    }