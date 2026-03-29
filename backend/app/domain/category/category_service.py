from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app.models.category import Category
from app.models.user import User


class CategoryService:

    @staticmethod
    def _get_category(db: Session, user: User, category_id: int):

        category = (
            db.query(Category)
            .filter(
                Category.id == category_id,
                Category.restaurant_id == user.restaurant_id
            )
            .first()
        )

        if not category:
            raise HTTPException(404, "Categoría no encontrada")

        return category


    @staticmethod
    def list_categories(db: Session, user: User):
        return (
            db.query(Category)
            .filter(Category.restaurant_id == user.restaurant_id)
            .order_by(Category.name)
            .all()
        )


    @staticmethod
    def create_category(db: Session, user: User, name: str):

        category = Category(
            name=name,
            restaurant_id=user.restaurant_id
        )

        db.add(category)
        db.commit()
        db.refresh(category)

        return category


    @staticmethod
    def update_category(db: Session, user: User, category_id: int, name: str):

        category = CategoryService._get_category(db, user, category_id)

        category.name = name

        db.commit()
        db.refresh(category)

        return category


    @staticmethod
    def delete_category(db: Session, user: User, category_id: int):

        category = CategoryService._get_category(db, user, category_id)

        db.delete(category)
        db.commit()

        return True


    @staticmethod
    def list_categories_with_products(db: Session, user: User):

        categories = (
            db.query(Category)
            .options(joinedload(Category.products))
            .filter(Category.restaurant_id == user.restaurant_id)
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
                if p.active and p.restaurant_id == user.restaurant_id
            ]

            result.append({
                "id": category.id,
                "name": category.name,
                "products": active_products
            })

        return result