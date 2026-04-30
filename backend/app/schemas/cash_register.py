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
    total_sales: Decimal
    orders_count: int
    average_ticket: Decimal
    by_method: dict[str, Decimal]

class PaymentBreakdown(BaseSchema):
    method: str
    total: Decimal


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
    amount: Decimal
    reason: str


class CashMovementOut(BaseSchema):
    id: int
    type: str
    amount: Decimal
    reason: str | None
    created_at: datetime


class CashRegisterDashboard(BaseSchema):
    cash_register_id: int
    opened_at: datetime
    opening_amount: Decimal
    total_sales: Decimal
    orders_count: int
    transactions_count: int
    average_ticket: Decimal
    by_method: dict[str, Decimal]
    cash_movements: list[CashMovementOut]
    expected_cash: Decimal


