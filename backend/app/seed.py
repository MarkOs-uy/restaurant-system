import logging
import os

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.restaurant import Restaurant
from app.models.user import User, UserRole

logger = logging.getLogger("app.seed")


# --------------------------------------------------------------------------------------
# Crea el restaurante por defecto si aún no existe.
# --------------------------------------------------------------------------------------
def seed_restaurant(db: Session) -> Restaurant:
    restaurant = db.query(Restaurant).first()
    if restaurant:
        logger.info("Default restaurant already exists.")
        return restaurant
    logger.info("Creating default restaurant.")
    restaurant = Restaurant(
        name="Resto Demo"
    )
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant

# --------------------------------------------------------------------------------------
# Crea el usuario administrador por defecto si aún no existe.
# --------------------------------------------------------------------------------------
def seed_admin(db: Session, restaurant: Restaurant,) -> None:
    admin = (
        db.query(User)
        .filter(
            User.restaurant_id == restaurant.id,
            User.username == "admin",
        )
        .first()
    )
    if admin:
        logger.info("Admin user already exists.")
        return
    admin_password = os.getenv("ADMIN_SEED_PASSWORD")
    if not admin_password:
        raise RuntimeError(
            "ADMIN_SEED_PASSWORD must be configured."
        )
    logger.info("Creating admin user.")
    db.add(
        User(
            username="admin",
            role=UserRole.ADMIN,
            password_hash=get_password_hash(admin_password),
            restaurant_id=restaurant.id,
            active=True,
        )
    )
    db.commit()
    logger.info("Admin user created successfully.")

# --------------------------------------------------------------------------------------
# Ejecuta el proceso completo de inicialización de datos.
# --------------------------------------------------------------------------------------
def run() -> None:
    db: Session = SessionLocal()
    try:
        restaurant = seed_restaurant(db)
        seed_admin(db, restaurant,)
    finally:

        db.close()

# --------------------------------------------------------------------------------------
# Punto de entrada del proceso de inicialización.
# --------------------------------------------------------------------------------------
if __name__ == "__main__":
    run()