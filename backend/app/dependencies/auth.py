from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class AuthError(Exception):
    pass


class AuthUser:

    def __init__(self, user: User):

        self.user = user
        self.id = user.id
        self.role = user.role
        self.restaurant_id = user.restaurant_id


def authenticate_token(db: Session, token: str) -> AuthUser:

    payload = decode_access_token(token)

    if not payload:
        raise AuthError("invalid token")

    try:
        user_id = int(payload.get("sub"))
        restaurant_id = int(payload.get("restaurant_id"))
        role = UserRole(payload.get("role"))
    except (TypeError, ValueError):
        raise AuthError("invalid token payload")

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.restaurant_id == restaurant_id
        )
        .first()
    )

    if not user:
        raise AuthError("user not found")

    if not user.active:
        raise AuthError("inactive user")

    if user.role != role:
        raise AuthError("role mismatch")

    return AuthUser(user)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    try:
        auth_user = authenticate_token(db, token)
    except AuthError as exc:
        if str(exc) == "inactive user":
            raise HTTPException(
                status_code=403,
                detail="Usuario inactivo"
            )
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )

    return auth_user.user
