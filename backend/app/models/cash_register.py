from sqlalchemy import Column, Integer, DateTime, Numeric, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CashRegister(Base):

    __tablename__ = "cash_registers"

    id = Column(Integer, primary_key=True)

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )

    is_open = Column(
        Boolean,
        default=True,
        nullable=False
    )

    opened_by_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    closed_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    opened_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    closed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    opening_amount = Column(
        Numeric(10,2),
        nullable=False
    )

    expected_cash = Column(
        Numeric(10,2),
        nullable=True
    )

    counted_cash = Column(
        Numeric(10,2),
        nullable=True
    )

    difference = Column(
        Numeric(10,2),
        nullable=True
    )

    total_sales = Column(
        Numeric(10,2),
        nullable=True
    )

    payments_snapshot = Column(JSON)

    # -------------------------
    # RELATIONSHIPS
    # -------------------------

    restaurant = relationship(
        "Restaurant",
        back_populates="cash_registers"
    )

    movements = relationship(
        "CashMovement",
        back_populates="cash_register",
        cascade="all, delete-orphan"
    )