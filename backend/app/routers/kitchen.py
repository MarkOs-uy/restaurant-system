"""
Endpoints para la gestión de la cocina.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import (
    APIRouter, 
    Depends, 
    status
)

from app.dependencies.roles import kitchen_or_admin

from app.domain.kitchen.dependencies import get_kitchen_service
from app.domain.kitchen.kitchen_service import KitchenService

from app.models.user import User

from app.schemas.order.kitchen import KitchenItemOut

router = APIRouter(prefix="/kitchen", tags=["kitchen"])

# ----------------------------------------------------------------------------------------------------
# Obtener items por estación
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/stations/{station_id}/items",
    response_model=list[KitchenItemOut],
    status_code=status.HTTP_200_OK,
    summary="Devolver items por estación",
    description="Devuelve la lista de items por estación del restaurante autenticado."
)
def get_station_items(
    station_id: int,
    user: User = Depends(kitchen_or_admin),
    service: KitchenService = Depends(get_kitchen_service)
):
    return service.get_station_items(
        station_id=station_id,
        user=user
    )