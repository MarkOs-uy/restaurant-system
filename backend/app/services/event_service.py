from sqlalchemy.orm import Session
from app.models.event_outbox import EventOutbox


class EventService:

    def __init__(self, db: Session):
        self.db = db

    def emit(
        self,
        restaurant_id: int,
        event_type: str,
        payload: dict,
        target: str = "broadcast",
        target_id: str | None = None
    ):
        event = EventOutbox(
            restaurant_id=restaurant_id,
            event_type=event_type,
            payload=payload,
            target=target,
            target_id=target_id,
            status="pending",
            retries=0
        )

        self.db.add(event)