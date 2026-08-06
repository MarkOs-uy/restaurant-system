import enum
import uuid
from sqlalchemy import Column, Integer, Numeric, ForeignKey, String, DateTime, Enum, Index, Identity
from sqlalchemy.sql import func
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class OrderStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    SENT = "SENT"
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, Identity(), primary_key=True, index=True)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)

    status = Column(
        Enum(OrderStatus),
        default=OrderStatus.OPEN,
        nullable=False
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime, nullable=True)
    discount = Column(Numeric(10, 2), nullable=False, default=0)
    external_id = Column(
        String,
        unique=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )    
    __table_args__ = (
        Index("ix_orders_restaurant_status", "restaurant_id", "status"),
    )
    table = relationship("Table", back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
