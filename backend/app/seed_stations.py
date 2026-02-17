from sqlalchemy.orm import Session
from app.models.production_station import ProductionStation
from app.seed_restaurant import seed_restaurant

def seed_stations(db: Session):

    restaurant = seed_restaurant(db)

    existing_stations = db.query(ProductionStation).count()

    if existing_stations > 0:
        print("Seed estaciones ya ejecutado.")
        return

    print("Creando estaciones iniciales...")

    products = [
        ProductionStation(name="Cocina", restaurant_id=restaurant.id),
        ProductionStation(name="Barra", restaurant_id=restaurant.id),
    ]

    db.add_all(products)
    db.commit()

    print("Estaciones creadas.")
