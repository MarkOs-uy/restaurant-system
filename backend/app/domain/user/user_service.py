from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserService:

    def __init__(self, db: Session):
        self.db = db


    def get_user(self, user_id: int, restaurant_id: int):

        user = self.db.query(User).filter(
            User.id == user_id,
            User.restaurant_id == restaurant_id
        ).first()

        if not user:
            raise HTTPException(404, "User not found")

        return user


    def list_users(self, restaurant_id: int):

        return self.db.query(User).filter(
            User.restaurant_id == restaurant_id
        ).all()


    def create_user(self, restaurant_id: int, data: UserCreate):

        hashed = get_password_hash(data.password)

        user = User(
            username=data.username,
            password_hash=hashed,
            role=data.role,
            restaurant_id=restaurant_id,
            active=True
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user


    def update_user(self, user_id: int, restaurant_id: int, data: UserUpdate):

        user = self.get_user(user_id, restaurant_id)

        if data.username is not None:
            user.username = data.username

        if data.role is not None:
            user.role = data.role

        if data.password:
            user.password_hash = get_password_hash(data.password)

        self.db.commit()
        self.db.refresh(user)

        return user


    def toggle_user(self, user_id: int, restaurant_id: int):

        user = self.get_user(user_id, restaurant_id)

        user.active = not user.active

        self.db.commit()
        self.db.refresh(user)

        return user