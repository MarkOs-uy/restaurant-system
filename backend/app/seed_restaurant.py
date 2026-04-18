from sqlalchemy.orm import Session
from app.models.restaurant import Restaurant


def seed_restaurant(db: Session):

    restaurant = db.query(Restaurant).first()

    if restaurant:
        print("Restaurant ya existe.")
        return restaurant

    print("Creando restaurant default...")
    restaurant = Restaurant(name="Resto Demo")

    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)

    return restaurant
