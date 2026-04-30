from decimal import Decimal

def decimal_to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return value

def decimal_dict_to_float(data: dict):
    return {k: decimal_to_float(v) for k, v in data.items()}