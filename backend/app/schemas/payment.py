from pydantic import BaseModel
from decimal import Decimal
from app.models.payment import PaymentMethod

class PaymentCreate(BaseModel):
    method: PaymentMethod
    amount: Decimal
