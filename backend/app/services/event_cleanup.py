import asyncio
import logging

from sqlalchemy import and_
from sqlalchemy.orm import Session

from datetime import datetime, timedelta, timezone

from app.db.session import SessionLocal
from app.models.event_outbox import EventOutbox

logger = logging.getLogger("app.event_cleanup")

# --------------------------------------------------------------------------------------
# Configuración
# --------------------------------------------------------------------------------------
PROCESSED_RETENTION_DAYS = 3
FAILED_RETENTION_DAYS = 7
FAILED_MAX_RETRIES = 10

# --------------------------------------------------------------------------------------
# Servicio encargado de eliminar eventos antiguos del EventOutbox.
# --------------------------------------------------------------------------------------
class EventCleanup:

    """
    Elimina periódicamente eventos antiguos del EventOutbox para evitar
    el crecimiento indefinido de la tabla.
    """
    
    def __init__(self, interval_seconds=3600) ->None:
        self.interval = interval_seconds

# --------------------------------------------------------------------------------------
# Ejecuta el proceso de limpieza periódicamente.
# --------------------------------------------------------------------------------------
    async def run(self) -> None:
        logger.info("Event cleanup job started")
        while True:
            try:
                await asyncio.sleep(self.interval)
                self.cleanup()
            except asyncio.CancelledError:
                logger.info("Event cleanup stopped")
                raise
            except Exception:
                logger.exception("Cleanup job failed")

# --------------------------------------------------------------------------------------
# Elimina eventos procesados y fallidos que ya no deben conservarse.
# --------------------------------------------------------------------------------------
    def cleanup(self) -> None:
        db: Session = SessionLocal()
        try:
            now = datetime.now(timezone.utc)
            processed_cutoff = now - timedelta(days=PROCESSED_RETENTION_DAYS)
            failed_cutoff = now - timedelta(days=FAILED_RETENTION_DAYS)
            # Eliminar eventos procesados antiguos.
            processed_deleted = (
                db.query(EventOutbox)
                .filter(
                    and_(
                        EventOutbox.status == "processed",
                        EventOutbox.processed_at < processed_cutoff
                    )
                )
                .delete(synchronize_session=False)
            )
            # Eliminar eventos fallidos que ya no volverán a reintentarse.
            failed_deleted = (
                db.query(EventOutbox)
                .filter(
                    and_(
                        EventOutbox.status == "failed",
                        EventOutbox.retries >= FAILED_MAX_RETRIES,
                        EventOutbox.created_at < failed_cutoff
                    )
                )
                .delete(synchronize_session=False)
            )
            db.commit()
            total = processed_deleted + failed_deleted
            if not total:
                return

            logger.info(
                "event_cleanup_completed processed=%s failed=%s total=%s",
                processed_deleted,
                failed_deleted,
                total,
            )
        except Exception:
            db.rollback()
            logger.exception("event_cleanup_failed")
        finally:
            db.close()