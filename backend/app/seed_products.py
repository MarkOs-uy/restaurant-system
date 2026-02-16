from sqlalchemy.orm import Session
from app.models.product import Product
from app.seed_restaurant import seed_restaurant

def seed_products(db: Session):

    restaurant = seed_restaurant(db)

    existing_products = db.query(Product).count()

    if existing_products > 0:
        print("Seed productos ya ejecutado.")
        return

    print("Creando productos iniciales...")

    products = [
        Product(name="Coca Cola", price=120, restaurant_id=restaurant.id),
        Product(name="Agua", price=90, restaurant_id=restaurant.id),
        Product(name="Cerveza", price=180, restaurant_id=restaurant.id),
        Product(name="Hamburguesa", price=450, restaurant_id=restaurant.id),
        Product(name="Pizza Muzza", price=520, restaurant_id=restaurant.id),
        Product(name="Papas Fritas", price=250, restaurant_id=restaurant.id),
    ]

    db.add_all(products)
    db.commit()

    print("Productos creados.")
