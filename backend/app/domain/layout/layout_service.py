import logging

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode
from app.domain.events.websocket import WSEvent

from app.services.event_service import EventService

from app.models.restaurant_layout import RestaurantLayout

from app.schemas.layout import LayoutUpdate

logger = logging.getLogger("app.domain.layout")

class LayoutService:

    """
    Servicio encargado de la lógica de negocio relacionada con el diseño del restaurante.

    Responsabilidades:
    - Gestionar la lógica de negocio del diseño del restaurante.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventService(db)

    # --------------------------------------------------------------------------------------
    # Validar imagen de fondo
    # --------------------------------------------------------------------------------------
    async def _validate_background_image(
        self,
        file: UploadFile
    ) -> tuple[bytes, str]:
        allowed_types = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/gif": ".gif"
        }
        extension = allowed_types.get(file.content_type or "")
        if not extension:
            raise DomainError(
                "Invalid image format. Allowed formats: JPEG, PNG, WEBP, GIF.",
                ErrorCode.LAYOUT_BACKGROUND_INVALID_FORMAT
            )
        content = await file.read()
        max_size = 8 * 1024 * 1024
        if len(content) > max_size:
            raise DomainError(
                "The image cannot exceed 8 MB.",
                ErrorCode.LAYOUT_BACKGROUND_TOO_LARGE
            )
        return content, extension

    # --------------------------------------------------------------------------------------
    # Guardar imagen de fondo
    # --------------------------------------------------------------------------------------
    def _save_background_image(
        self,
        restaurant_id: int,
        content: bytes,
        extension: str
    ) -> str:
        upload_root = (
            Path(__file__).resolve().parents[3]
            / "uploads"
            / "layouts"
        )
        restaurant_dir = upload_root / str(restaurant_id)
        restaurant_dir.mkdir(
            parents=True,
            exist_ok=True
        )
        filename = f"{uuid4().hex}{extension}"
        destination = restaurant_dir / filename
        try:
            destination.write_bytes(content)
        except OSError:
            logger.exception(
                "No se pudo guardar la imagen de fondo del layout. "
                "restaurant_id=%s",
                restaurant_id
            )
            raise
        return f"/uploads/layouts/{restaurant_id}/{filename}"

    # --------------------------------------------------------------------------------------
    # Devuelve el diseño del restaurante, si no existe lo crea con valores por defecto
    # --------------------------------------------------------------------------------------
    def get_layout(self, restaurant_id: int) -> RestaurantLayout:
        layout = (
            self.db.query(RestaurantLayout)
            .filter(RestaurantLayout.restaurant_id == restaurant_id)
            .first()
        )
        if not layout:
            layout = RestaurantLayout(
                restaurant_id=restaurant_id,
                width=900,
                height=750,
                grid_size=40,
                snap_to_grid=True
            )
            self.db.add(layout)
            self.db.commit()
            self.db.refresh(layout)
        return layout

    # --------------------------------------------------------------------------------------
    # Actualiza el diseño del restaurante
    # --------------------------------------------------------------------------------------
    def update_layout(self, restaurant_id: int, data: LayoutUpdate) -> RestaurantLayout:
        logger.info("Layout actualizado r=%s", restaurant_id)
        layout = self.get_layout(restaurant_id)
        layout.width = data.width
        layout.height = data.height
        layout.grid_size = data.grid_size
        layout.snap_to_grid = data.snap_to_grid
        if data.background_image is not None:
            layout.background_image = data.background_image
        self.db.refresh(layout)
        self.events.emit(
                restaurant_id=restaurant_id,
                event_type=WSEvent.LAYOUT_UPDATED,
                payload={"restaurant_id": restaurant_id}
            )
        self.db.commit()
        return layout

    # --------------------------------------------------------------------------------------
    # Actualiza la imagen de fondo del diseño del restaurante
    # --------------------------------------------------------------------------------------
    async def update_background_image(
        self,
        restaurant_id: int,
        file: UploadFile
    ) -> RestaurantLayout:
        logger.info(
            "Background del layout actualizado r=%s",
            restaurant_id
        )
        content, extension = await self._validate_background_image(file)
        background_image = self._save_background_image(
            restaurant_id,
            content,
            extension
        )
        layout = self.get_layout(restaurant_id)
        layout.background_image = background_image
        self.events.emit(
            restaurant_id=restaurant_id,
            event_type=WSEvent.LAYOUT_UPDATED,
            payload={
                "restaurant_id": restaurant_id
            }
        )
        self.db.commit()
        self.db.refresh(layout)
        return layout