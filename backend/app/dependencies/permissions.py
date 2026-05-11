from fastapi import Depends
from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode
from app.models.user import UserRole
from app.models.user import User
from app.dependencies.auth import get_current_user


def require_roles(*roles: UserRole):
    def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise DomainError(
                "No tienes permisos para realizar esta acción",
                ErrorCode.PERMISSION_DENIED,
                context={
                    "required_roles": [r.value for r in roles],
                    "user_role": user.role.value
                }
            )
        return user

    return role_checker