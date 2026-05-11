import asyncio
import logging

from sqlalchemy import delete, and_
from datetime import datetime, timedelta

from app.db.session import SessionLocal
from app.models.event_outbox import EventOutbox

logger = logging.getLogger("app.services.event_cleanup")


class EventCleanup:

    def __init__(self, interval_seconds=3600):
        self.interval = interval_seconds

    async def run(self):

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

def cleanup(self):

    db = SessionLocal()

    try:

        now = datetime.utcnow()

        sent_cutoff = now - timedelta(days=3)
        failed_cutoff = now - timedelta(days=7)

        # ---------------------------------
        # borrar eventos ya enviados
        # ---------------------------------

        sent_deleted = (
            db.query(EventOutbox)
            .filter(
                and_(
                    EventOutbox.status == "sent",
                    EventOutbox.processed_at < sent_cutoff
                )
            )
            .delete(synchronize_session=False)
        )

        # ---------------------------------
        # borrar eventos fallidos irrecuperables
        # ---------------------------------

        failed_deleted = (
            db.query(EventOutbox)
            .filter(
                and_(
                    EventOutbox.status == "failed",
                    EventOutbox.retries >= 10,
                    EventOutbox.created_at < failed_cutoff
                )
            )
            .delete(synchronize_session=False)
        )

        db.commit()

        total = sent_deleted + failed_deleted

        if total > 0:
            logger.info(
                "event_cleanup_completed",
                extra={
                    "sent_deleted": sent_deleted,
                    "failed_deleted": failed_deleted,
                    "total_deleted": total
                }
            )

    except Exception:

        db.rollback()

        logger.exception("event_cleanup_failed")

    finally:

        db.close()