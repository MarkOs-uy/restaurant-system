from sqlalchemy.orm import Session, joinedload

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode


class ProductService:

    """
    Servicio encargado de la lógica de negocio relacionada con los productos.

    Responsabilidades:
    - Gestionar el CRUD de productos.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # -------------------------
    # Obtener producto
    # -------------------------
    def _get_product(self, product_id: int, restaurant_id: int) -> Product:
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

    # --------------------------------------------------------------------------------
    # Encontrar producto por nombre
    # --------------------------------------------------------------------------------
    def _product_name_exists(
        self,
        restaurant_id: int,
        name: str,
        exclude_id: int | None = None
    ) -> bool:
        query = (
            self.db.query(Product)
            .filter(
                Product.restaurant_id == restaurant_id,
                Product.name == name
            )
        )
        if exclude_id is not None:
            query = query.filter(Product.id != exclude_id)
        return query.first() is not None

    # -------------------------
    # Crear producto
    # -------------------------
    def create_product(self, restaurant_id: int, data: ProductCreate) -> Product:
        name = data.name.strip()
        if not name:
            raise DomainError(
                "Product name cannot be empty",
                ErrorCode.INVALID_PRODUCT_NAME
            )
        existing = self._product_name_exists(restaurant_id, name)
        if existing:
            raise DomainError(
                "Product already exists",
                ErrorCode.PRODUCT_ALREADY_EXISTS
            )
        product = Product(
            name=name,
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
    def list_products(self, restaurant_id: int) -> list[Product]:
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
    def update_product(self, product_id: int, restaurant_id: int, data: ProductUpdate) -> Product:
        product = self._get_product(product_id, restaurant_id)
        if data.name is not None:
            name = data.name.strip()
            if not name:
                raise DomainError(
                    "Product name cannot be empty",
                    ErrorCode.INVALID_PRODUCT_NAME
                )
            existing = self._product_name_exists(restaurant_id, name, exclude_id=product.id)
            if existing:
                raise DomainError(
                    "Product already exists",
                    ErrorCode.PRODUCT_ALREADY_EXISTS
                )
            data.name = name
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        self.db.commit()
        self.db.refresh(product)
        return product

    # -------------------------------------
    # Cambiar producto - Activo/Inactivo
    # -------------------------------------
    def toggle_product(self, product_id: int, restaurant_id: int) -> Product:
        product = self._get_product(product_id, restaurant_id)
        product.active = not product.active
        self.db.commit()
        self.db.refresh(product)
        return product