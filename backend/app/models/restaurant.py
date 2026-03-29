from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.base_class import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    active = Column(Boolean, default=True, nullable=False)

    plan = Column(String, default="basic", nullable=False)

    external_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    # Relaciones
    tables = relationship("Table", back_populates="restaurant", cascade="all, delete")
    products = relationship("Product", back_populates="restaurant", cascade="all, delete")
    payments = relationship("Payment", back_populates="restaurant", cascade="all, delete")
    orders = relationship("Order", back_populates="restaurant", cascade="all, delete")
    cash_registers = relationship("CashRegister", back_populates="restaurant", cascade="all, delete")
    stations = relationship("ProductionStation", back_populates="restaurant", cascade="all, delete")
    categories = relationship("Category", back_populates="restaurant", cascade="all, delete")
    order_items = relationship("OrderItem", back_populates="restaurant", cascade="all, delete")
    users = relationship("User", back_populates="restaurant")
    domain_events = relationship("DomainEvent", back_populates="restaurant")


