import logging

from sqlalchemy.orm import Session, joinedload

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.models.category import Category

from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryWithProducts
)
from app.schemas.category import ProductRef

logger = logging.getLogger("app.domain.category")

class CategoryService:

    """
    Servicio encargado de la lógica de negocio relacionada con las categorías.

    Responsabilidades:
    - Gestionar el CRUD de categorías.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # --------------------------------------------------------------------------------
    # Obtener una categoría del restaurante o lanzar DomainError si no existe
    # --------------------------------------------------------------------------------
    def _get_category(
        self,
        restaurant_id: int,
        category_id: int
    ) -> Category:
        category = (
            self.db.query(Category)
            .filter(
                Category.id == category_id,
                Category.restaurant_id == restaurant_id
            )
            .first()
        )
        if not category:
            raise DomainError(
                "Category not found",
                ErrorCode.CATEGORY_NOT_FOUND
            )
        return category

    # --------------------------------------------------------------------------------
    # Encontrar categoría por nombre
    # --------------------------------------------------------------------------------
    def _category_name_exists(
        self,
        restaurant_id: int,
        name: str,
        exclude_id: int | None = None
    ) -> bool:
        query = (
            self.db.query(Category)
            .filter(
                Category.restaurant_id == restaurant_id,
                Category.name == name
            )
        )
        if exclude_id is not None:
            query = query.filter(Category.id != exclude_id)
        return query.first() is not None
    
    # -------------------------
    # Listar categorías
    # -------------------------
    def list_categories(
        self,
        restaurant_id: int,
        active: bool | None = True
    ) -> list[Category]:
        query = (
            self.db.query(Category)
            .filter(Category.restaurant_id == restaurant_id)
        )
        if active is not None:
            query = query.filter(Category.active == active)
        return query.order_by(Category.name).all()

    # -------------------------
    # Crear categoría
    # -------------------------
    def create_category(
        self,
        restaurant_id: int,
        data: CategoryCreate
    ) -> Category:
        name = data.name.strip()
        if not name:
            raise DomainError(
                "Category name cannot be empty",
                ErrorCode.INVALID_CATEGORY_NAME
            )
        existing = self._category_name_exists(restaurant_id, name)
        if existing:
            raise DomainError(
                "Category already exists",
                ErrorCode.CATEGORY_ALREADY_EXISTS
            )
        category = Category(
            name=name,
            restaurant_id=restaurant_id
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category
        
    # -------------------------
    # Actualizar categoría
    # -------------------------
    def update_category(
        self,
        restaurant_id: int,
        category_id: int,
        data: CategoryUpdate
    ) -> Category:
        name = data.name.strip()
        if not name:
            raise DomainError(
                "Category name cannot be empty",
                ErrorCode.INVALID_CATEGORY_NAME
            )
        existing = self._category_name_exists(restaurant_id, name, exclude_id=category_id)
        if existing:
            raise DomainError(
                "Category already exists",
                ErrorCode.CATEGORY_ALREADY_EXISTS
            )
        category = self._get_category(restaurant_id, category_id)
        category.name = name
        self.db.commit()
        self.db.refresh(category)
        return category

    # -------------------------
    # Eliminar categoría
    # -------------------------
    def delete_category(
        self,
        restaurant_id: int,
        category_id: int
    ) -> None:
        category = self._get_category(restaurant_id, category_id)
        self.db.delete(category)
        self.db.commit()

    # --------------------------------------------
    # Activar o desactivar categoría
    # --------------------------------------------
    def toggle_category(
        self,
        restaurant_id: int,
        category_id: int
    ) -> Category:
        category = self._get_category(restaurant_id, category_id)
        category.active = not category.active
        self.db.commit()
        self.db.refresh(category)
        logger.info(
            "Categoría alternada r=%s category_id=%s active=%s",
            restaurant_id,
            category.id,
            category.active
        )
        return category

    # --------------------------------------------
    # Listar categorías con productos activos
    # --------------------------------------------
    def list_categories_with_products(
        self,
        restaurant_id: int
    ) -> list[CategoryWithProducts]:
        categories = (
            self.db.query(Category)
            .options(joinedload(Category.products))
            .filter(Category.restaurant_id == restaurant_id)
            .filter(Category.active.is_(True))
            .order_by(Category.name)
            .all()
        )
        return [
            CategoryWithProducts(
                id=c.id,
                name=c.name,
                products=[
                    ProductRef(
                        id=p.id,
                        name=p.name,
                        price=p.price
                    )
                    for p in c.products
                    if p.active
                ]
            )
            for c in categories
        ]