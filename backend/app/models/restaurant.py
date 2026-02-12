from sqlalchemy import Column, Integer, String, DateTime, Boolean
import uuid
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
from datetime import datetime, timezone


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    active = Column(Boolean, default=True)

    plan = Column(String, default="basic")  

    external_id = Column(
        String,
        unique=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )


    tables = relationship("Table", back_populates="restaurant")
    products = relationship("Product", back_populates="restaurant")
    payments = relationship("Payment", back_populates="restaurant")
    orders = relationship("Order", back_populates="restaurant")
    order_items = relationship("OrderItem", back_populates="restaurant")
    cash_registers = relationship("CashRegister", back_populates="restaurant")