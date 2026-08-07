from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.domain.backup.backup_service import BackupService
from app.scheduler.scheduler import scheduler


# --------------------------------------------------------------------------------------
# Registra las tareas programadas relacionadas con los backups.
# --------------------------------------------------------------------------------------
def register_jobs() -> None:
    scheduler.add_job(
        scheduled_backup_job,
        trigger="interval",
        minutes=1,
        id="backup_scheduler",
        replace_existing=True,
    )


# --------------------------------------------------------------------------------------
# Ejecuta la comprobación de backups pendientes.
# Crea una sesión independiente de base de datos para el scheduler.
# --------------------------------------------------------------------------------------
def scheduled_backup_job() -> None:

    db: Session = SessionLocal()

    try:
        BackupService(db).run_pending_backups()

    finally:
        db.close()