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

    print("Creando usuario admin...")

    pass_hash = get_password_hash("1234")

    users = [
        User(username="admin", role="ADMIN", password_hash = pass_hash, restaurant_id=restaurant.id),
        #User(username="waiter", role="WAITER", password_hash = pass_hash, restaurant_id=restaurant.id),
        #User(username="kitchen", role="KITCHEN", password_hash = pass_hash, restaurant_id=restaurant.id),
        #User(username="cashier", role="CASHIER", password_hash = pass_hash, restaurant_id=restaurant.id),
    ]

    db.add_all(users)
    db.commit()

    print("Usuario Admin creado.")
