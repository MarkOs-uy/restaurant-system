from sqlalchemy.orm import Session
from app.models.table import Table
from app.seed_restaurant import seed_restaurant


def seed_tables(db: Session):

    restaurant = seed_restaurant(db)

    existing_tables = db.query(Table).count()

    if existing_tables > 0:
        print("Seed ya ejecutado. No se crean mesas.")
        return

    print("Creando mesas iniciales...")

    tables = [
        Table(number=i, restaurant_id=restaurant.id)
        for i in range(1, 21)
    ]

    db.add_all(tables)
    db.commit()

    print("Mesas creadas.")
