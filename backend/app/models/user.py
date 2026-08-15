import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    Boolean,
    Identity,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    WAITER = "WAITER"
    KITCHEN = "KITCHEN"
    CASHIER = "CASHIER"


class User(Base):
    __tablename__ = "users"

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

    username = Column(
        String,
        nullable=False
    )

    role = Column(
        Enum(UserRole),
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "username",
            name="uq_user_username_per_restaurant"
        ),
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="users"
    )