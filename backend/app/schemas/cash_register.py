from pydantic import BaseModel
from decimal import Decimal

class CashRegisterOpen(BaseModel):
    opening_amount: Decimal
