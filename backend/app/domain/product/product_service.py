from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:

    def __init__(self, db: Session):
        self.db = db

    def get_product(self, product_id: int, restaurant_id: int):

        product = self.db.query(Product).filter(
            Product.id == product_id,
            Product.restaurant_id == restaurant_id
        ).first()

        if not product:
            raise HTTPException(404, "Product not found")

        return product


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


    def update_product(self, product_id: int, restaurant_id: int, data: ProductUpdate):

        product = self.get_product(product_id, restaurant_id)

        if data.name is not None:
            product.name = data.name

        if data.price is not None:
            product.price = data.price

        if data.category_id is not None:
            product.category_id = data.category_id

        if data.station_id is not None:
            product.station_id = data.station_id

        self.db.commit()
        self.db.refresh(product)

        return product


    def toggle_product(self, product_id: int, restaurant_id: int):

        product = self.get_product(product_id, restaurant_id)

        product.active = not product.active

        self.db.commit()
        self.db.refresh(product)

        return product