import logging
from sqlalchemy.orm import Session

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.core.security import get_password_hash

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger("app.domain.user")

class UserService:

    def __init__(self, db: Session) -> None:
        self.db = db

    # -----------------------------------------------------------------
    # Verificar si un nombre de usuario ya existe en el restaurante
    # -----------------------------------------------------------------
    def _username_exists(
        self,
        restaurant_id: int,
        username: str,
        exclude_user_id: int | None = None
    ) -> bool:
        query = self.db.query(User).filter(
            User.restaurant_id == restaurant_id,
            User.username == username
        )
        if exclude_user_id is not None:
            query = query.filter(User.id != exclude_user_id)
        return query.first() is not None

    # -------------------------
    # Obtener usuario
    # -------------------------
    def get_user(self, user_id: int, restaurant_id: int) -> User:
        user = self.db.query(User).filter(
            User.id == user_id,
            User.restaurant_id == restaurant_id
        ).first()
        if not user:
            raise DomainError(
                "User not found",
                ErrorCode.USER_NOT_FOUND
            )
        return user

    # -------------------------
    # Listar usuarios
    # -------------------------
    def list_users(self, restaurant_id: int) -> list[User]:
        return (
            self.db.query(User)
            .filter(User.restaurant_id == restaurant_id)
            .order_by(User.username)
            .all()
        )

    # -------------------------
    # Crear usuario
    # -------------------------
    def create_user(self, restaurant_id: int, data: UserCreate) -> User:
        existing = self._username_exists(restaurant_id, data.username)
        if existing:
            raise DomainError(
                "User exists",
                ErrorCode.USERNAME_ALREADY_EXISTS,
                context={"username": data.username}
            )
        hashed = get_password_hash(data.password.get_secret_value())
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
        logger.info(
            "Usuario creado r=%s username=%s role=%s",
            restaurant_id,
            user.username,
            user.role
        )
        return user

    # -------------------------
    # Actualizar usuario
    # -------------------------
    def update_user(self, user_id: int, restaurant_id: int, data: UserUpdate) -> User:
        user = self.get_user(user_id, restaurant_id)
        if data.username is not None:
            existing = self._username_exists(restaurant_id, data.username, exclude_user_id=user_id)
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
            user.password_hash = get_password_hash(data.password.get_secret_value())
        self.db.commit()
        self.db.refresh(user)
        logger.info(
            "Usuario actualizado r=%s id=%s",
            restaurant_id,
            user.id
        )
        return user

    # --------------------------------------
    # Activar / Desactivar usuario
    # --------------------------------------
    def toggle_user(self, target_user_id: int, current_user_id: int, restaurant_id: int) -> User:
        if target_user_id == current_user_id:
            raise DomainError(
                "You cannot deactivate your own account.",
                ErrorCode.USER_CANNOT_DEACTIVATE_SELF
            )
        user = self.get_user(target_user_id, restaurant_id)
        user.active = not user.active
        self.db.commit()
        self.db.refresh(user)
        logger.info(
            "Usuario %s id=%s",
            "activado" if user.active else "desactivado",
            restaurant_id,
            user.id
        )
        return user