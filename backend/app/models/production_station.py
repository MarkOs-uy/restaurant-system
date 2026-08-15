from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Boolean, 
    ForeignKey, 
    UniqueConstraint, 
    Identity
)
from app.db.base_class import Base

class ProductionStation(Base):
    __tablename__ = "production_stations"

    id = Column(Integer, Identity(), primary_key=True)
    restaurant_id = Column(ForeignKey("restaurants.id"), nullable=False)
    name = Column(String, nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("restaurant_id", "name", name="uq_station_name_per_restaurant"),
    )
    restaurant = relationship("Restaurant", back_populates="stations")
    products = relationship("Product", back_populates="station")
