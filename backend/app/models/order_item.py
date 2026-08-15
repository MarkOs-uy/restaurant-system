from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    String,
    Enum,
    Identity,
    Index
)
from sqlalchemy.orm import relationship
import enum

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

    id = Column(
        Integer,
        Identity(),
        primary_key=True
    )

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    unit_price = Column(
        Numeric(10, 2),
        nullable=False
    )

    status = Column(
        Enum(OrderItemStatus),
        default=OrderItemStatus.PENDING,
        nullable=False
    )

    notes = Column(
        String,
        nullable=True
    )

    __table_args__ = (
        Index(
            "ix_order_items_order_status",
            "order_id",
            "status"
        ),
    )

    order = relationship(
        "Order",
        back_populates="items"
    )

    product = relationship("Product")

    restaurant = relationship(
        "Restaurant",
        back_populates="order_items"
    )