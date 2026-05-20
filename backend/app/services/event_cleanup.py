import asyncio
import logging

from sqlalchemy import and_
from datetime import datetime, timedelta, timezone

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

            now = datetime.now(timezone.utc)

            processed_cutoff = now - timedelta(days=3)
            failed_cutoff = now - timedelta(days=7)

            # borrar processed viejos
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

            # borrar failed irreparables
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

            total = processed_deleted + failed_deleted

            if total > 0:
                logger.info(
                    "event_cleanup_completed processed=%s failed=%s total=%s",
                    processed_deleted, failed_deleted, total
                )

        except Exception:

            db.rollback()
            logger.exception("event_cleanup_failed")

        finally:

            db.close()