from app.models.user import UserRole
from app.dependencies.permissions import require_roles

admin_only = require_roles(UserRole.ADMIN)
waiter_or_admin = require_roles(UserRole.ADMIN, UserRole.WAITER)
cashier_or_admin = require_roles(UserRole.ADMIN, UserRole.CASHIER)
kitchen_or_admin = require_roles(UserRole.ADMIN, UserRole.KITCHEN)
waiter_kitchen_or_admin = require_roles(UserRole.ADMIN, UserRole.WAITER, UserRole.KITCHEN)
waiter_cashier_or_admin = require_roles(UserRole.ADMIN, UserRole.WAITER, UserRole.CASHIER)
all_staff = require_roles(UserRole.ADMIN, UserRole.WAITER, UserRole.KITCHEN, UserRole.CASHIER)