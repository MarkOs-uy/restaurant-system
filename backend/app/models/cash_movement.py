import enum

from sqlalchemy import Column, Integer, DateTime, Numeric, ForeignKey, Enum, String, Identity
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CashMovementType(str, enum.Enum):
    CASH_IN = "cash_in"
    CASH_OUT = "cash_out"


class CashMovement(Base):

    __tablename__ = "cash_movements"

    id = Column(Integer, Identity(), primary_key=True)

    cash_register_id = Column(
        Integer,
        ForeignKey("cash_registers.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    type = Column(
        Enum(CashMovementType),
        nullable=False
    )

    amount = Column(Numeric(10,2))

    reason = Column(String(255))

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    cash_register = relationship(
        "CashRegister",
        back_populates="movements"
    )