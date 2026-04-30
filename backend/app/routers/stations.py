from fastapi import APIRouter, Depends
from app.models.user import User

from app.domain.stations.dependencies import get_station_service
from app.domain.stations.station_service import StationService

from app.schemas.station import StationCreate, StationOut, StationUpdate
from app.schemas.order.kitchen import KitchenItemOut

from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/stations", tags=["stations"])


@router.post("/", response_model=StationOut)
def create_station(
    data: StationCreate,
    user: User = Depends(get_current_user),
    service: StationService = Depends(get_station_service)
):
    return service.create_station(
        user.restaurant_id,
        data.name
    )


@router.get("/", response_model=list[StationOut])
def list_stations(
    user: User = Depends(get_current_user),
    service: StationService = Depends(get_station_service)
):
    return service.list_stations(user.restaurant_id)


@router.get("/active", response_model=list[StationOut])
def list_active_stations(
    user: User = Depends(get_current_user),
    service: StationService = Depends(get_station_service)
):
    return service.list_active_stations(user.restaurant_id)


@router.get("/{station_id}", response_model=StationOut)
def get_station(
    station_id: int,
    user: User = Depends(get_current_user),
    service: StationService = Depends(get_station_service)
):
    return service.get_station(user.restaurant_id, station_id)


@router.patch("/{station_id}")
def update_station(
    station_id: int,
    data: StationUpdate,
    user: User = Depends(get_current_user),
    service: StationService = Depends(get_station_service)
):
    return service.update_station(
        user.restaurant_id,
        station_id,
        data.name
    )


@router.patch("/{station_id}/toggle")
def toggle_station(
    station_id: int,
    user: User = Depends(get_current_user),
    service: StationService = Depends(get_station_service)
):
    return service.toggle_station(
        user.restaurant_id,
        station_id
    )


@router.get("/stations/{station_id}/items", response_model=list[KitchenItemOut])
def get_station_items(
    station_id: int,
    user: User = Depends(get_current_user),
    service: StationService = Depends(get_station_service)
):
    return service.get_station_items(
        user.restaurant_id,
        station_id
    )