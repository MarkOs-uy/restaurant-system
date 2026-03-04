from sqlalchemy.orm import Session
from app.models.user import User
from app.seed_restaurant import seed_restaurant
from app.core.security import get_password_hash

def seed_users(db: Session):

    restaurant = seed_restaurant(db)

    existing_users = db.query(User).count()

    if existing_users > 0:
        print("Seed usuarios ya ejecutado.")
        return

    print("Creando usuarios iniciales...")

    pass_hash = get_password_hash("1234")

    users = [
        User(name="admin", role="ADMIN", password_hash = pass_hash, restaurant_id=restaurant.id),
        User(name="waiter", role="WAITER", password_hash = pass_hash, restaurant_id=restaurant.id),
        User(name="kitchen", role="KITCHEN", password_hash = pass_hash, restaurant_id=restaurant.id),
        User(name="cashier", role="CASHIER", password_hash = pass_hash, restaurant_id=restaurant.id),
    ]

    db.add_all(users)
    db.commit()

    print("Estaciones creadas.")
