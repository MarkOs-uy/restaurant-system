from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app.models.category import Category
from app.models.user import User


class CategoryService:

    def __init__(self, db: Session):
        self.db = db

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
            raise HTTPException(404, "Categoría no encontrada")

        return category


    def list_categories(self, restaurant_id: int):
        return (
            self.db.query(Category)
            .filter(Category.restaurant_id == restaurant_id)
            .order_by(Category.name)
            .all()
        )


    def create_category(self, restaurant_id: int, name: str):

        category = Category(
            name=name,
            restaurant_id=restaurant_id
        )

        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        return category


    def update_category(self, restaurant_id: int, category_id: int, name: str):

        category = self._get_category(restaurant_id, category_id)

        category.name = name

        self.db.commit()
        self.db.refresh(category)

        return category


    def delete_category(self, restaurant_id: int, category_id: int):

        category = self._get_category(restaurant_id, category_id)

        self.db.delete(category)
        self.db.commit()

        return True


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