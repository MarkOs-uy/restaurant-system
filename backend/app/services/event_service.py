from typing import Any

from sqlalchemy.orm import Session

from app.models.event_outbox import EventOutbox


class EventService:
    """
    Servicio encargado de registrar eventos en la tabla EventOutbox.

    Los eventos son procesados posteriormente por el EventWorker,
    que los publica en Redis y actualiza su estado.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # --------------------------------------------------------------------------------------
    # Registra un evento pendiente para ser procesado por el EventWorker.
    # --------------------------------------------------------------------------------------
    def emit(
        self,
        restaurant_id: int,
        event_type: str,
        payload: dict[str, Any],
        target: str = "broadcast",
        target_id: str | None = None,
    ) -> None:

        event = EventOutbox(
            restaurant_id=restaurant_id,
            event_type=event_type,
            payload=payload,
            target=target,
            target_id=target_id,
            status="pending",
            retries=0,
        )

        self.db.add(event)