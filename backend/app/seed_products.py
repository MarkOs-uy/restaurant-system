from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.category import Category
from app.seed_restaurant import seed_restaurant


def seed_products(db: Session):

    restaurant = seed_restaurant(db)

    existing_products = db.query(Product).count()
    if existing_products > 0:
        print("Seed productos ya ejecutado.")
        return

    print("Creando categorías iniciales...")

    # Crear categorías
    bebidas = Category(name="Bebidas", restaurant_id=restaurant.id)
    cocina = Category(name="Cocina", restaurant_id=restaurant.id)

    db.add_all([bebidas, cocina])
    db.commit()

    db.refresh(bebidas)
    db.refresh(cocina)

    print("Creando productos iniciales...")

    products = [
        # BEBIDAS → estación 2 (barra)
        Product(
            name="Coca Cola",
            price=120,
            restaurant_id=restaurant.id,
            station_id=2,
            category_id=bebidas.id
        ),
        Product(
            name="Agua",
            price=90,
            restaurant_id=restaurant.id,
            station_id=2,
            category_id=bebidas.id
        ),
        Product(
            name="Cerveza",
            price=180,
            restaurant_id=restaurant.id,
            station_id=2,
            category_id=bebidas.id
        ),

        # COCINA → estación 1
        Product(
            name="Hamburguesa",
            price=450,
            restaurant_id=restaurant.id,
            station_id=1,
            category_id=cocina.id
        ),
        Product(
            name="Pizza Muzza",
            price=520,
            restaurant_id=restaurant.id,
            station_id=1,
            category_id=cocina.id
        ),
        Product(
            name="Papas Fritas",
            price=250,
            restaurant_id=restaurant.id,
            station_id=1,
            category_id=cocina.id
        ),
    ]

    db.add_all(products)
    db.commit()

    print("Productos creados con categorías.")
