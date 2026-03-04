from decimal import Decimal
from app.models.payment import PaymentMethod
from ..base import BaseSchema

class PaymentCreate(BaseSchema):
    method: PaymentMethod
    amount: Decimal


class PaymentOut(BaseSchema):
    id: int
    amount: Decimal
    method: PaymentMethod