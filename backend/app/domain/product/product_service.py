from sqlalchemy.orm import Session, joinedload

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode


class ProductService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Obtener producto
    # -------------------------

    def get_product(self, product_id: int, restaurant_id: int):
        product = self.db.query(Product).filter(
            Product.id == product_id,
            Product.restaurant_id == restaurant_id
        ).first()
        if not product:
            raise DomainError(
                "Product not found",
                ErrorCode.PRODUCT_NOT_FOUND,
                context={"product_id": product_id})
        return product

    # -------------------------
    # Crear producto
    # -------------------------

    def create_product(self, restaurant_id: int, data: ProductCreate):
        product = Product(
            name=data.name,
            price=data.price,
            category_id=data.category_id,
            station_id=data.station_id,
            restaurant_id=restaurant_id
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    # -------------------------
    # Listar productos
    # -------------------------

    def list_products(self, restaurant_id: int):
        return (
            self.db.query(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.station)
            )
            .filter(Product.restaurant_id == restaurant_id)
            .all()
        )

    # -------------------------
    # Actualizar producto
    # -------------------------

    def update_product(self, product_id: int, restaurant_id: int, data: ProductUpdate):
        product = self.get_product(product_id, restaurant_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        self.db.commit()
        self.db.refresh(product)
        return product

    # -------------------------
    # Cambiar producto - Activo/Inactivo
    # -------------------------

    def toggle_product(self, product_id: int, restaurant_id: int):
        product = self.get_product(product_id, restaurant_id)
        product.active = not product.active
        self.db.commit()
        self.db.refresh(product)
        return product