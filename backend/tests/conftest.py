"""
conftest.py

Fixtures compartidas para toda la suite de tests.
pytest descubre este archivo automáticamente (no hace falta importarlo).

Ubicación esperada: backend/tests/conftest.py
"""

import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base_class import Base

from app.models.restaurant import Restaurant
from app.models.user import User, UserRole
from app.models.table import Table
from app.models.category import Category
from app.models.production_station import ProductionStation
from app.models.product import Product
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem, OrderItemStatus


@pytest.fixture
def db():
    """
    Sesión de base de datos aislada por test.

    SQLite in-memory: no toca Postgres, no requiere el contenedor `db`
    levantado, y se descarta automáticamente al terminar el test.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def restaurant(db):
    """
    Restaurante base para asociar a las entidades de cada test.
    Ajustar los campos si Restaurant exige más columnas obligatorias.
    """
    r = Restaurant(name="Restaurante de Prueba")
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@pytest.fixture
def user(db, restaurant):
    """
    Usuario base (cajero) para operaciones que requieren user_id.
    """
    u = User(
        restaurant_id=restaurant.id,
        username="cajero_test",
        role=UserRole.CASHIER,
        password_hash="x",  # placeholder, no se testea login en estos tests
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def table(db, restaurant):
    """
    Mesa base -- Order.table_id es obligatorio, así que toda orden
    de prueba necesita una mesa asociada.
    """
    t = Table(
        restaurant_id=restaurant.id,
        number=1,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@pytest.fixture
def product(db, restaurant):
    """
    Producto base para armar OrderItems. Encadena Category y
    ProductionStation porque Product los exige como FK obligatoria,
    aunque la lógica de order_service no los use directamente.
    """
    category = Category(restaurant_id=restaurant.id, name="Categoría Test")
    station = ProductionStation(restaurant_id=restaurant.id, name="Estación Test")
    db.add_all([category, station])
    db.commit()
    db.refresh(category)
    db.refresh(station)

    p = Product(
        restaurant_id=restaurant.id,
        name="Producto Test",
        price=Decimal("100.00"),
        station_id=station.id,
        category_id=category.id,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@pytest.fixture
def order(db, restaurant, table):
    """
    Orden vacía (sin items) en estado OPEN, lista para que cada test
    le agregue los items/pagos que necesite.
    """
    o = Order(
        restaurant_id=restaurant.id,
        table_id=table.id,
        status=OrderStatus.OPEN,
    )
    db.add(o)
    db.commit()
    db.refresh(o)
    return o