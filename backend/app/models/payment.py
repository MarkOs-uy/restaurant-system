import enum
from sqlalchemy import Column, Integer, Enum, Numeric, ForeignKey, Identity
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    CARD = "CARD"
    TRANSFER = "TRANSFER"
    OTHER = "OTHER"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, Identity(), primary_key=True)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    amount = Column(Numeric(10,2), nullable=False)
    cash_register_id = Column(
        Integer,
        ForeignKey("cash_registers.id"),
        nullable=False
    )
    order = relationship("Order", back_populates="payments")
    cash_register = relationship("CashRegister")
    restaurant = relationship("Restaurant", back_populates="payments")



