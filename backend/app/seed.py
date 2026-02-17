from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.table import Table
from app.seed_restaurant import seed_restaurant
from app.seed_products import seed_products
from app.seed_stations import seed_stations


def seed_tables(db: Session):

    restaurant = seed_restaurant(db)

    if db.query(Table).first():
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

def run():
    db = SessionLocal()
    try:
        seed_tables(db)
        seed_stations(db)
        seed_products(db)
    finally:
        db.close()


if __name__ == "__main__":
    run()
