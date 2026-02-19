import enum
from sqlalchemy import Column, Integer, ForeignKey, Numeric, String, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class OrderItemStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10,2), nullable=False)

    status = Column(Enum(OrderItemStatus), default=OrderItemStatus.PENDING, nullable=False)
    notes = Column(String, nullable=True)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
