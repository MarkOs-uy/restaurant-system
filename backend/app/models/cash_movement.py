import enum

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Numeric,
    ForeignKey,
    Enum,
    String,
    Identity,
    Index
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CashMovementType(str, enum.Enum):
    CASH_IN = "cash_in"
    CASH_OUT = "cash_out"


class CashMovement(Base):
    __tablename__ = "cash_movements"

    id = Column(
        Integer,
        Identity(),
        primary_key=True
    )

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
        Enum(
            CashMovementType,
            values_callable=lambda enum: [
                item.value
                for item in enum
            ],
            native_enum=False,
            length=20
        ),
        nullable=False
    )

    amount = Column(
        Numeric(10, 2),
        nullable=False
    )

    reason = Column(
        String(255),
        nullable=True
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    __table_args__ = (
        Index(
            "ix_cash_movements_register",
            "cash_register_id"
        ),
        Index(
            "ix_cash_movements_register_type",
            "cash_register_id",
            "type"
        ),
    )

    cash_register = relationship(
        "CashRegister",
        back_populates="movements"
    )