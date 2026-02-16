import uuid
from sqlalchemy import Column, Integer, Boolean, ForeignKey, String
from app.db.base_class import Base
from sqlalchemy.orm import relationship


class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )
    number = Column(Integer, unique=True, nullable=False)
    active = Column(Boolean, default=True)
    external_id = Column(
        String,
        unique=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )
    orders = relationship("Order", back_populates="table")
    restaurant = relationship("Restaurant", back_populates="tables")



