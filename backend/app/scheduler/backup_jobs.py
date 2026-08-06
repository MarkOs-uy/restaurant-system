from app.scheduler.scheduler import scheduler
from app.db.session import SessionLocal
from app.domain.backup.backup_service import BackupService


def register_jobs():
    scheduler.add_job(
        scheduled_backup_job,
        trigger="interval",
        minutes=1,
        id="backup_scheduler",
        replace_existing=True,
    )

def scheduled_backup_job():

    db = SessionLocal()

    try:
        service = BackupService(db)
        service.run_pending_backups()

    finally:
        db.close()
