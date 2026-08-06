"""
Endpoints para la gestión de la caja registradora.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import APIRouter, Depends, status

from app.dependencies.roles import cashier_or_admin

from app.domain.cash_register.cash_register_service import CashRegisterService
from app.domain.cash_register.cash_movement_service import CashMovementService
from app.domain.cash_register.dependencies import (
    get_cash_register_service,
    get_cash_movement_service
)

from app.models.user import User

from app.schemas.cash_register import (
    CashRegisterOpen,
    CashRegisterResponse,
    CashRegisterSummary,
    CashRegisterCloseOut,
    CashMovementCreate,
    CashMovementOut,
    CashRegisterClose,
    CashRegisterDashboard
)

router = APIRouter(prefix="/cash-register", tags=["cash-register"])

# ----------------------------------------------------------------------------------------------------
# Abrir caja registradora
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/open",
    response_model=CashRegisterResponse,
    status_code=status.HTTP_200_OK,
    summary="Abre caja registradora",
    description="Abre una caja registradora con un monto inicial en el restaurant autenticado."
    )

def open_cash_register(
    data: CashRegisterOpen,
    user: User = Depends(cashier_or_admin),
    service: CashRegisterService = Depends(get_cash_register_service),
):
    return service.open_cash_register(
        restaurant_id=user.restaurant_id,
        user_id=user.id,
        opening_amount=data.opening_amount
    )

# ----------------------------------------------------------------------------------------------------
# Cerrar caja registradora
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/close",
    response_model=CashRegisterCloseOut,
    status_code=status.HTTP_200_OK,
    summary="Cierra una caja registradora",
    description="Cierra la caja registradora del restaurant autenticado."
)
def close_cash_register(
    data: CashRegisterClose,
    user: User = Depends(cashier_or_admin),
    service: CashRegisterService = Depends(get_cash_register_service)   
):
    return service.close_cash_register(
        restaurant_id=user.restaurant_id,
        user_id=user.id,
        data=data
    )

# ----------------------------------------------------------------------------------------------------
# Agregar un movimiento de caja
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/movements",
    response_model=CashMovementOut,
    status_code=status.HTTP_201_CREATED,
    summary="Agrega un movimiento de caja",
    description="Agrega un movimiento de caja para el restaurant autenticado."
)
def create_cash_movement(
    data: CashMovementCreate,
    user: User = Depends(cashier_or_admin),
    service: CashMovementService = Depends(get_cash_movement_service)
):
    return service.create_cash_movement(
        restaurant_id=user.restaurant_id,
        user_id=user.id,
        data=data
    )

# ----------------------------------------------------------------------------------------------------
# Devuelve un resumen de la caja actual
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/current",
    response_model=CashRegisterSummary | None,
    status_code=status.HTTP_200_OK,
    summary="Resumen de la caja actual",
    description="Obtener un resumen de la caja actual del restaurant autenticado."
)
def current_cash_register(
    service: CashRegisterService = Depends(get_cash_register_service),
    user: User = Depends(cashier_or_admin)
):
    return service.get_current_cash_register(
        restaurant_id=user.restaurant_id
    )

# ----------------------------------------------------------------------------------------------------
# Devuelve un resumen para el dashboard de la página del cajero
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/dashboard",
    response_model=CashRegisterDashboard | None,
    status_code=status.HTTP_200_OK,
    summary="Obtener dashboard",
    description="Obtener resumen de la caja actual para el dashboard de la página del cajero del restaurant autenticado."
)
def get_cash_register_dashboard(
    service: CashRegisterService = Depends(get_cash_register_service),
    user: User = Depends(cashier_or_admin)
):
    return service.get_dashboard(
        restaurant_id=user.restaurant_id
    )

# ----------------------------------------------------------------------------------------------------
# Eliminar un movimiento de caja
# ----------------------------------------------------------------------------------------------------
@router.delete(
    "/movements/{movement_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar un movimiento de caja",
    description="Elimina un movimientod de caja para el restaurant autenticado."
)
def delete_cash_movement(
    movement_id: int,
    user: User = Depends(cashier_or_admin),
    service: CashMovementService = Depends(get_cash_movement_service),
):
    return service.delete_cash_movement(
        restaurant_id=user.restaurant_id,
        movement_id=movement_id
    )