"""
Endpoints para la gestión de estaciones.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import (
    APIRouter,
    status, 
    Depends, 
    Query
)

from app.dependencies.roles import (
    admin_only, 
    kitchen_or_admin
)

from app.domain.stations.dependencies import get_station_service
from app.domain.stations.station_service import StationService

from app.models.user import User

from app.schemas.station import (
    StationCreate,
    StationResponse,
    StationUpdate,
)

router = APIRouter(prefix="/stations", tags=["stations"])

# ----------------------------------------------------------------------------------------------------
# Crear estación
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/",
    response_model=StationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear estación",
    description="Crea una nueva estación para el restaurante autenticado."
)
def create_station(
    data: StationCreate,
    user: User = Depends(admin_only),
    service: StationService = Depends(get_station_service)
):
    return service.create_station(user.restaurant_id, data)

# ----------------------------------------------------------------------------------------------------
# Listar estaciones
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/",
    response_model=list[StationResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar estaciones",
    description="Devuelve la lista de estaciones del restaurante autenticado."
)
def list_stations(
    active: bool | None = Query(default=True),
    user: User = Depends(kitchen_or_admin),
    service: StationService = Depends(get_station_service)
):
    return service.list_stations(user.restaurant_id, active)

# ----------------------------------------------------------------------------------------------------
# Listar estaciones activas
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/active",
    response_model=list[StationResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar estaciones activas",
    description="Devuelve la lista de estaciones activas del restaurante autenticado."
)
def list_active_stations(
    user: User = Depends(kitchen_or_admin),
    service: StationService = Depends(get_station_service)
):
    return service.list_stations(user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Obtener estación
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/{station_id}",
    response_model=StationResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener estación",
    description="Devuelve una estación específica del restaurante autenticado."
)
def get_station(
    station_id: int,
    user: User = Depends(kitchen_or_admin),
    service: StationService = Depends(get_station_service)
):
    return service.get_station(user.restaurant_id, station_id)

# ----------------------------------------------------------------------------------------------------
# Actualizar estación
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{station_id}",
    response_model=StationResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar estación",
    description="Actualiza la información de una estación específica del restaurante autenticado."
)
def update_station(
    station_id: int,
    data: StationUpdate,
    user: User = Depends(admin_only),
    service: StationService = Depends(get_station_service)
):
    return service.update_station(user.restaurant_id, station_id, data)

# ----------------------------------------------------------------------------------------------------
# Alternar estado de estación
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{station_id}/toggle",
    response_model=StationResponse,
    status_code=status.HTTP_200_OK,
    summary="Alternar estado de estación",
    description="Alterna el estado de una estación específica del restaurante autenticado."
)
def toggle_station(
    station_id: int,
    user: User = Depends(admin_only),
    service: StationService = Depends(get_station_service)
):
    return service.toggle_station(user.restaurant_id, station_id)