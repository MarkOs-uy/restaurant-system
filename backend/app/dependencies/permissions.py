from fastapi import Depends

from app.dependencies.auth import get_current_user

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.models.user import User, UserRole

# --------------------------------------------------------------------------------------
# Crea una dependencia que restringe el acceso a uno o más roles.
#
# Uso:
#   admin_only = require_roles(UserRole.ADMIN)
#   admin_or_cashier = require_roles(UserRole.ADMIN, UserRole.CASHIER)
# --------------------------------------------------------------------------------------
def require_roles(*roles: UserRole):

    # ----------------------------------------------------------------------------------
    # Verifica que el usuario autenticado tenga alguno de los roles permitidos.
    # ----------------------------------------------------------------------------------
    def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise DomainError(
                "Permission denied",
                ErrorCode.PERMISSION_DENIED,
                context={
                    "required_roles": [role.value for role in roles],
                    "user_role": user.role.value
                }
            )
        return user
    return role_checker