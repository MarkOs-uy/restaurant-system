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

class PaymentBreakdown(BaseSchema):
    method: str
    total: float


class CashRegisterCloseOut(BaseSchema):
    message: str
    total_sales: Decimal
    transactions_count: int
    by_method: list[PaymentBreakdown]
    opening_amount: Decimal
    expected_cash: Decimal
    counted_cash: Decimal
    difference: Decimal


class CashRegisterClose(BaseSchema):
    counted_cash: Decimal


class CashMovementCreate(BaseSchema):
    type: str
    amount: float
    reason: str


class CashRegisterDashboard(BaseSchema):

    cash_register_id: int
    opened_at: datetime

    opening_amount: Decimal

    total_sales: float
    orders_count: int
    average_ticket: float

    by_method: dict[str, float]

    cash_movements: list[dict]

    expected_cash: float