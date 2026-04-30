from sqlalchemy.orm import Session, joinedload
from app.models.category import Category
from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

class CategoryService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Devolver una categoría, lanzar error si no existe o no pertenece al restaurante
    # -------------------------

    def _get_category(self, restaurant_id: int, category_id: int):
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

    # -------------------------
    # Listar categorías
    # -------------------------

    def list_categories(self, restaurant_id: int):
        return (
            self.db.query(Category)
            .filter(Category.restaurant_id == restaurant_id)
            .order_by(Category.name)
            .all()
        )

    # -------------------------
    # Crear categoría
    # -------------------------

    def create_category(self, restaurant_id: int, name: str):
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

    def update_category(self, restaurant_id: int, category_id: int, name: str):
        category = self._get_category(restaurant_id, category_id)
        category.name = name
        self.db.commit()
        self.db.refresh(category)
        return category

    # -------------------------
    # Eliminar categoría
    # -------------------------

    def delete_category(self, restaurant_id: int, category_id: int):
        category = self._get_category(restaurant_id, category_id)
        self.db.delete(category)
        self.db.commit()
        return True

    # -------------------------
    # Listar categorías con productos activos
    # -------------------------

    def list_categories_with_products(self, restaurant_id: int):
        categories = (
            self.db.query(Category)
            .options(joinedload(Category.products))
            .filter(Category.restaurant_id == restaurant_id)
            .order_by(Category.name)
            .all()
        )
        result = []
        for category in categories:
            active_products = [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price
                }
                for p in category.products
                if p.active
            ]
            result.append({
                "id": category.id,
                "name": category.name,
                "products": active_products
            })
        return result