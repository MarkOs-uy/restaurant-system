from sqlalchemy import Column, Integer, DateTime, Numeric, ForeignKey
from sqlalchemy.sql import func
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class CashRegister(Base):
    __tablename__ = "cash_registers"

    id = Column(Integer, primary_key=True)
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)

    opening_amount = Column(Numeric(10,2), nullable=False)
    closing_amount = Column(Numeric(10,2), nullable=True)

    restaurant = relationship("Restaurant", back_populates="cash_registers")