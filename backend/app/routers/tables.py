"""
Endpoints para la gestión de mesas.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import (
    APIRouter, 
    Depends, 
    status,
    Query
)

from app.dependencies.roles import (
    waiter_or_admin, 
    admin_only
)

from app.domain.table.table_service import TableService
from app.domain.table.dependencies import get_table_service
from app.domain.order.order_service import OrderService
from app.domain.order.dependencies import get_order_service

from app.models.user import User

from app.schemas.table import (
    TableCreate,
    TableResponse,
    TableUpdate,
    TableList,
    TableStatusResponse,
    TablePositionUpdate,
    TablePositionOut,
    TableTouchResponse
)

from app.schemas.order.order_item import OrderItemCreate

router = APIRouter(prefix="/tables", tags=["tables"])

# ----------------------------------------------------------------------------------------------------
# Crear mesa
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/",
    response_model=TableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear mesa",
    description="Crea una nueva mesa para el restaurante autenticado."
)
def create_table(
    data: TableCreate,
    user: User = Depends(admin_only),
    service: TableService = Depends(get_table_service)
):
    return service.create_table(user.restaurant_id, data)

# ----------------------------------------------------------------------------------------------------
# Tocar mesa
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/{table_id}/touch",
    response_model=TableTouchResponse,
    status_code=status.HTTP_200_OK,
    summary="Tocar mesa",
    description="Accede a una mesa para realizar operaciones."
)
def touch_table(
    table_id: int,
    user: User = Depends(waiter_or_admin),
    service: TableService = Depends(get_table_service)
):
    return service.touch_table(user.restaurant_id, table_id)

# ----------------------------------------------------------------------------------------------------
# Agregar producto a la orden de la mesa
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/{table_id}/add-product",
    status_code=status.HTTP_200_OK,
    summary="Agregar producto a la orden",
    description="Agrega un producto a la orden abierta de una mesa."
)
def add_product_to_order(
    table_id: int,
    data: OrderItemCreate,
    user: User = Depends(waiter_or_admin),
    service: OrderService = Depends(get_order_service)
):
    return service.add_product_to_order(
        restaurant_id=user.restaurant_id,
        table_id=table_id,
        data=data
    )

# ----------------------------------------------------------------------------------------------------
# Listar mesas
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/",
    response_model=list[TableList],
    status_code=status.HTTP_200_OK,
    summary="Listar mesas",
    description="Lista todas las mesas del restaurante autenticado."
)
def list_tables(
    active: bool | None = Query(default=True),
    user: User = Depends(waiter_or_admin),
    service: TableService = Depends(get_table_service)
):
    return service.list_tables(user.restaurant_id, active)

# ----------------------------------------------------------------------------------------------------
# Listar estado de las mesas
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/status",
    response_model=list[TableStatusResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar estado de las mesas",
    description="Lista el estado de todas las mesas del restaurante autenticado."
)
def list_tables_status(
    user: User = Depends(waiter_or_admin),
    service: TableService = Depends(get_table_service)
):
    return service.list_tables_status(user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Modificar posición de la mesa
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{table_id}/position",
    response_model=TablePositionOut,
    status_code=status.HTTP_200_OK,
    summary="Modificar posición de la mesa",
    description="Modifica la posición de una mesa específica del restaurante autenticado."
)
def update_position(
    table_id: int,
    data: TablePositionUpdate,
    user: User = Depends(admin_only),
    service: TableService = Depends(get_table_service)
):
    return service.update_position(user.restaurant_id, table_id, data)

# ----------------------------------------------------------------------------------------------------
# Activar mesa
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{table_id}/activate",
    status_code=status.HTTP_200_OK,
    summary="Activar mesa",
    description="Activa una mesa específica del restaurante autenticado."
)
def activate_table(
    table_id: int,
    user: User = Depends(admin_only),
    service: TableService = Depends(get_table_service)
):
    return service.activate_table(user.restaurant_id, table_id)

# ----------------------------------------------------------------------------------------------------
# Actualizar mesa
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{table_id}",
    response_model=TableResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar mesa",
    description="Actualiza la información de una mesa específica del restaurante autenticado."
)
def update_table(
    table_id: int,
    data: TableUpdate,
    user: User = Depends(admin_only),
    service: TableService = Depends(get_table_service)
):
    return service.update_table(user.restaurant_id, table_id, data)

# ----------------------------------------------------------------------------------------------------
# Desactivar mesa
# ----------------------------------------------------------------------------------------------------
@router.delete(
    "/{table_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar mesa",
    description="Desactiva una mesa específica del restaurante autenticado."
)
def deactivate_table(
    table_id: int,
    user: User = Depends(admin_only),
    service: TableService = Depends(get_table_service)
):
    return service.deactivate_table(user.restaurant_id, table_id)