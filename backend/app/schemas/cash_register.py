from datetime import datetime
from decimal import Decimal
from .base import BaseSchema


class CashRegisterOpen(BaseSchema):
    opening_amount: Decimal


class CashRegisterOut(BaseSchema):
    id: int
    restaurant_id: int
    opening_amount: Decimal
    closing_amount: Decimal | None
    opened_at: datetime
    closed_at: datetime | None
    is_open: bool
    opened_by_id: int
    closed_by_id: int | None

class CashRegisterSummary(BaseSchema):
    cash_register_id: int
    opened_at: datetime
    total_sales: float
    orders_count: int
    average_ticket: float
    by_method: dict[str, float]

class CashRegisterCloseOut(BaseSchema):
    message: str
    total_vendido: Decimal