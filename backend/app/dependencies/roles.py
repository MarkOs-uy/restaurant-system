from app.dependencies.permissions import require_roles

from app.models.user import UserRole

# --------------------------------------------------------------------------------------
# Dependencias reutilizables para autorización basada en roles.
# --------------------------------------------------------------------------------------

admin_only = require_roles(UserRole.ADMIN)

waiter_or_admin = require_roles(
    UserRole.ADMIN,
    UserRole.WAITER
)

cashier_or_admin = require_roles(
    UserRole.ADMIN,
    UserRole.CASHIER
)

kitchen_or_admin = require_roles(
    UserRole.ADMIN,
    UserRole.KITCHEN
)

waiter_cashier_or_admin = require_roles(
    UserRole.ADMIN,
    UserRole.WAITER,
    UserRole.CASHIER
)

waiter_kitchen_or_admin = require_roles(
    UserRole.ADMIN,
    UserRole.WAITER,
    UserRole.KITCHEN
)

all_staff = require_roles(
    UserRole.ADMIN,
    UserRole.WAITER,
    UserRole.CASHIER,
    UserRole.KITCHEN
)