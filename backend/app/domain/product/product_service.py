from sqlalchemy.orm import Session, joinedload

from app.models.product import Product
from app.models.category import Category
from app.models.production_station import ProductionStation
from app.schemas.product import (
    ProductCreate, 
    ProductUpdate
)

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

    # --------------------------------------------------------------------------------
    # Obtener una categoría activa del restaurante o lanzar DomainError si no existe
    # --------------------------------------------------------------------------------
    def _get_active_category(
        self,
        restaurant_id: int,
        category_id: int
    ) -> Category:
        category = (
            self.db.query(Category)
            .filter(
                Category.id == category_id,
                Category.restaurant_id == restaurant_id,
                Category.active.is_(True)
            )
            .first()
        )

        if not category:
            raise DomainError(
                "Category not found or inactive",
                ErrorCode.CATEGORY_NOT_FOUND,
                context={"category_id": category_id}
            )

        return category


    # --------------------------------------------------------------------------------
    # Obtener una estación activa del restaurante o lanzar DomainError si no existe
    # --------------------------------------------------------------------------------
    def _get_active_station(
        self,
        restaurant_id: int,
        station_id: int
    ) -> ProductionStation:
        station = (
            self.db.query(ProductionStation)
            .filter(
                ProductionStation.id == station_id,
                ProductionStation.restaurant_id == restaurant_id,
                ProductionStation.active.is_(True)
            )
            .first()
        )

        if not station:
            raise DomainError(
                "Station not found or inactive",
                ErrorCode.STATION_NOT_FOUND,
                context={"station_id": station_id}
            )

        return station

    # -------------------------
    # Crear producto
    # -------------------------
    def create_product(
        self,
        restaurant_id: int,
        data: ProductCreate
    ) -> Product:

        name = data.name.strip()

        if not name:
            raise DomainError(
                "Product name cannot be empty",
                ErrorCode.INVALID_PRODUCT_NAME
            )

        if self._product_name_exists(
            restaurant_id,
            name
        ):
            raise DomainError(
                "Product already exists",
                ErrorCode.PRODUCT_ALREADY_EXISTS
            )

        self._get_active_category(
            restaurant_id,
            data.category_id
        )

        self._get_active_station(
            restaurant_id,
            data.station_id
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
    def list_products(
        self,
        restaurant_id: int,
        active: bool | None = True
    ) -> list[Product]:

        query = (
            self.db.query(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.station)
            )
            .filter(
                Product.restaurant_id == restaurant_id
            )
        )

        if active is not None:
            query = query.filter(
                Product.active == active
            )

        return (
            query
            .order_by(Product.name)
            .all()
        )

    # -------------------------
    # Actualizar producto
    # -------------------------
    def update_product(
        self,
        product_id: int,
        restaurant_id: int,
        data: ProductUpdate
    ) -> Product:

        product = self._get_product(
            product_id,
            restaurant_id
        )

        if data.name is not None:
            name = data.name.strip()

            if not name:
                raise DomainError(
                    "Product name cannot be empty",
                    ErrorCode.INVALID_PRODUCT_NAME
                )

            existing = self._product_name_exists(
                restaurant_id,
                name,
                exclude_id=product.id
            )

            if existing:
                raise DomainError(
                    "Product already exists",
                    ErrorCode.PRODUCT_ALREADY_EXISTS
                )

            data.name = name

        if data.category_id is not None:
            self._get_active_category(
                restaurant_id,
                data.category_id
            )

        if data.station_id is not None:
            self._get_active_station(
                restaurant_id,
                data.station_id
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

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