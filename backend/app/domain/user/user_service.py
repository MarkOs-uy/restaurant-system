from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode


class UserService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Obtener usuario
    # -------------------------

    def get_user(self, user_id: int, restaurant_id: int):
        user = self.db.query(User).filter(
            User.id == user_id,
            User.restaurant_id == restaurant_id
        ).first()
        if not user:
            raise DomainError(
                "User not found",
                code=ErrorCode.USER_NOT_FOUND
            )
        return user


    # -------------------------
    # Listar usuarios
    # -------------------------

    def list_users(self, restaurant_id: int):
        return (
            self.db.query(User)
            .filter(User.restaurant_id == restaurant_id)
            .order_by(User.username)
            .all()
        )


    # -------------------------
    # Crear usuario
    # -------------------------

    def create_user(self, restaurant_id: int, data: UserCreate):
        existing = self.db.query(User).filter(
            User.restaurant_id == restaurant_id,
            User.username == data.username
        ).first()
        if existing:
            raise DomainError(
                "User exists",
                ErrorCode.USERNAME_ALREADY_EXISTS,
                context={"username": data.username}
            )
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


    # -------------------------
    # Actualizar usuario
    # -------------------------

    def update_user(self, user_id: int, restaurant_id: int, data: UserUpdate):
        user = self.get_user(user_id, restaurant_id)
        if data.username is not None:
            existing = self.db.query(User).filter(
                User.restaurant_id == restaurant_id,
                User.username == data.username,
                User.id != user_id
            ).first()
            if existing:
                raise DomainError(
                    "User exists",
                    ErrorCode.USERNAME_ALREADY_EXISTS,
                    context={"username": data.username}
                )
            user.username = data.username
        if data.role is not None:
            user.role = data.role
        if data.password is not None:
            user.password_hash = get_password_hash(data.password)
        self.db.commit()
        self.db.refresh(user)
        return user


    # -------------------------
    # Activar / Desactivar usuario
    # -------------------------

    def toggle_user(self, user_id: int, restaurant_id: int):
        user = self.get_user(user_id, restaurant_id)
        user.active = not user.active
        self.db.commit()
        self.db.refresh(user)
        return user