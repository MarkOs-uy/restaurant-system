import enum
from sqlalchemy import Column, Integer, Enum, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    CARD = "CARD"
    TRANSFER = "TRANSFER"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    cash_register_id = Column(
        Integer,
        ForeignKey("cash_registers.id"),
        nullable=False
    )
    order = relationship("Order", back_populates="payment")
    cash_register = relationship("CashRegister")
    restaurant = relationship("Restaurant", back_populates="payments")



