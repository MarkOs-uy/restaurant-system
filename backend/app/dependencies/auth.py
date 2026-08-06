from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token

from app.db.session import get_db

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.models.user import (
    User,
    UserRole
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ---------------------------------------------------------------------------------------------
# Autentica un token y devuelve el usuario correspondiente.
# Lanza DomainError si el token es inválido, el usuario no existe o no puede autenticarse.
# ---------------------------------------------------------------------------------------------
def authenticate_token(
    db: Session,
    token: str
) -> User:

    payload = decode_access_token(token)

    if not payload:
        raise DomainError(
            "Invalid token",
            ErrorCode.INVALID_TOKEN
        )

    try:
        user_id = int(payload["sub"])
        restaurant_id = int(payload["restaurant_id"])
        role = UserRole(payload["role"])

    except (KeyError, TypeError, ValueError):
        raise DomainError(
            "Invalid token payload",
            ErrorCode.INVALID_TOKEN_PAYLOAD
        )

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.restaurant_id == restaurant_id
        )
        .first()
    )

    if not user:
        raise DomainError(
            "User not found",
            ErrorCode.USER_NOT_FOUND
        )

    if not user.active:
        raise DomainError(
            "Inactive user",
            ErrorCode.USER_INACTIVE
        )

    if user.role != role:
        raise DomainError(
            "Role mismatch",
            ErrorCode.ROLE_MISMATCH
        )

    return user


# ---------------------------------------------------------------------------------------------
# Obtiene el usuario autenticado a partir del token de acceso.
# Lanza DomainError si el token es inválido o el usuario no puede autenticarse.
# ---------------------------------------------------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    return authenticate_token(
        db=db,
        token=token
    )