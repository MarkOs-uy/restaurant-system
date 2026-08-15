from sqlalchemy.orm import Session

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.models.production_station import ProductionStation

from app.schemas.station import (
    StationCreate,
    StationUpdate
)

class StationService:

    """
    Servicio encargado de la lógica de negocio relacionada con las estaciones.

    Responsabilidades:
    - Gestionar el CRUD de estaciones.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # -------------------------------------------------------
    # Comprobar si el nombre de la estación ya existe
    # -------------------------------------------------------
    def _station_name_exists(
        self,
        restaurant_id: int,
        name: str,
        exclude_id: int | None = None
    ) -> bool:
        query = (
            self.db.query(ProductionStation)
            .filter(
                ProductionStation.restaurant_id == restaurant_id,
                ProductionStation.name == name
            )
        )
        if exclude_id is not None:
            query = query.filter(
                ProductionStation.id != exclude_id
            )
        return query.first() is not None

    # ---------------------------------------
    # Obtener estación - método privado
    # ---------------------------------------
    def _get_station(self, restaurant_id: int, station_id: int) -> ProductionStation:
        station = (
            self.db.query(ProductionStation)
            .filter(
                ProductionStation.id == station_id,
                ProductionStation.restaurant_id == restaurant_id
            )
            .first()
        )
        if not station:
            raise DomainError(
                "Station not found",
                code=ErrorCode.STATION_NOT_FOUND
            )
        return station

    # -------------------------
    # Obtener estación
    # -------------------------
    def get_station(
        self,
        restaurant_id: int,
        station_id: int
    ):
        return self._get_station(
            restaurant_id,
            station_id
        )

    # -------------------------
    # Crear estación
    # ------------------------- 
    def create_station(self, restaurant_id: int, data: StationCreate) -> ProductionStation:
        name=data.name.strip()
        if not name:
            raise DomainError(
                "Station name cannot be empty",
                ErrorCode.INVALID_STATION_NAME
            )

        if self._station_name_exists(restaurant_id, name):
            raise DomainError(
                "Station name already exists",
                ErrorCode.STATION_NAME_ALREADY_EXISTS,
                context={"name": name}
            )
        station = ProductionStation(
            name=name,
            restaurant_id=restaurant_id,
            active=True
        )
        self.db.add(station)
        self.db.commit()
        self.db.refresh(station)
        return station
    
    # -------------------------
    # Listar estaciones
    # -------------------------
    def list_stations(
        self,
        restaurant_id: int,
        active: bool | None = True
    ) -> list[ProductionStation]:

        query = (
            self.db.query(ProductionStation)
            .filter(
                ProductionStation.restaurant_id == restaurant_id
            )
        )

        if active is not None:
            query = query.filter(
                ProductionStation.active == active
            )

        return (
            query
            .order_by(ProductionStation.name)
            .all()
        )

    # -------------------------
    # Actualizar estación
    # -------------------------
    def update_station(self, restaurant_id: int, station_id: int, data: StationUpdate) -> ProductionStation:
        station = self._get_station(restaurant_id, station_id)
        name = data.name.strip()
        if not name:
            raise DomainError(
                "Station name cannot be empty",
                ErrorCode.INVALID_STATION_NAME
            )
        if self._station_name_exists(
            restaurant_id,
            name,
            exclude_id=station_id
        ):
            raise DomainError(
                "Station name already exists",
                ErrorCode.STATION_NAME_ALREADY_EXISTS,
                context={"name": name}
            )
        station.name = name
        self.db.commit()
        self.db.refresh(station)
        return station

    # -----------------------------
    # Activar/desactivar estación
    # -----------------------------
    def toggle_station(self, restaurant_id: int, station_id: int) -> ProductionStation:
        station = self._get_station(restaurant_id, station_id)
        station.active = not station.active
        self.db.commit()
        self.db.refresh(station)
        return station