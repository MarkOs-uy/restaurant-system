from app.db.base_class import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class ProductionStation(Base):
    __tablename__ = "production_stations"

    id = Column(Integer, primary_key=True)
    restaurant_id = Column(ForeignKey("restaurants.id"), nullable=False)
    name = Column(String, nullable=False)
    active = Column(Boolean, default=True)

    restaurant = relationship("Restaurant", back_populates="stations")
    products = relationship("Product", back_populates="station")
